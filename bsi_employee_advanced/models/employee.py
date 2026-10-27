from odoo import api,fields,models
from odoo.exceptions import UserError,ValidationError

class TestEmployee(models.Model):
    _name = 'test.employee'
    _description = 'Employee'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(required=True,tracking=True)
    code = fields.Char(string='Employee Code',copy=False)
    department_id = fields.Many2one('test.department',string='Department',tracking=True)
    user_id = fields.Many2one('res.users',string='User')
    salary =fields.Float(string='Monthly Salary',tracking=True)
    joining_date = fields.Date()
    date_of_birth = fields.Date()
    active = fields.Boolean(default=True)
    status = fields.Selection(
        [('probation','Probation'),
        ('confirmed','Confirmed'),
        ('resigned','Resigned')],default='probation',required=True,tracking=True)
    
    age = fields.Integer(compute='_compute_age')
    service_days = fields.Integer(compute='_compute_service_days')
    annual_salary = fields.Float(compute='_compute_annual_salary',store=True)
    bonus = fields.Float(compute='_compute_bonus')

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_of_birth:
                days = (today-rec.date_of_birth).days
                rec.age = int(days/365.25)
            else:
                rec.age = 0

    @api.depends('joining_date')
    def _compute_service_days(self):
        today = fields.Date.today()
        for rec in self:
            if rec.joining_date:
                rec.service_days = (today-rec.joining_date).days
            else:
                rec.service_days=0

    @api.depends('salary')
    def _compute_annual_salary(self):
        for rec in self:
            rec.annual_salary = rec.salary * 12
    
    @api.depends('annual_salary','service_days')
    def _compute_bonus(self):
        for rec in self:
            if rec.service_days >=365 :
                rec.bonus = rec.annual_salary * 0.10
            else:
                rec.bonus = 0

    @api.constrains('date_of_birth')
    def _check_minimum_age(self):
        for rec in self:
            if rec.date_of_birth and rec.age < 18 :
                raise ValidationError("Employee must be at least 18 years old.")
    
    @api.constrains('joining_date')
    def _check_joining_date(self):
        for rec in self:
            if rec.joining_date and rec.joining_date > fields.Date.today():
                raise ValidationError("Joining date cannot be in future.")

    @api.constrains('salary')
    def _check_salary(self):
        for rec in self:
            if rec.salary < 0:
                raise ValidationError("Employee's salary cannot be negative.")

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('test.employee')
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.status != 'probation':
                raise UserError("Employee in probation can be confirmed.")
            rec.status = 'confirmed'

    def action_resign(self):
        for rec in self:
            if rec.status != 'confirmed':
                raise UserError("Confirmed Employee can resign.")
        rec.status = 'resigned'

    def write(self,vals):
        if 'salary' in vals and not self.env.context.get('salary_revision'):
            for rec in self:
                if rec.status == 'confirmed':
                    raise UserError("Salary of a confirmed employee can not be changed.")
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.status == 'confirmed':
                    raise UserError("Confirmed employees cannot be deleted.")
        return super().unlink()

    # task 10 & 11

    def _cron_anniversary_review(self):
        today = fields.Date.today()
        summary = "Anniversary review %s" %today.strftime('%B %Y')

        employees = self.search([('joining_date', '!=' , False)])

        for emp in employees:
            if emp.joining_date.month != today.month :
                continue
            
            if emp.joining_date.year != today.year :
                continue

            manager  = emp.department_id.manager_id
            if not manager :
                continue
            
            if emp.activity_ids.filtered(lambda a: a.summary == summary):
                continue

            years = today.year - emp.joining_date.year

            emp.activity_schedule(
                'mail.mail_activity_data_todo',
                summary = summary,
                note = f"{emp.name} completes {years} years this month.",
                user_id = manager_id,
            )

    def _cron_confirm_probation(self):
        employees = self.search([
            ('status' , '=' , 'probation'),
            ('joining_date' , '!=' , False),
        ])

        for emp in employees:
            if emp.service_days >= 90:
                emp.action_confirm()
                emp.message_post(body = "Automatically confirmed aftrr 90  days of service.")