from datetime import date
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _name = 'bsi.employee'
    _description = 'Employee'

    name = fields.Char(string='Employee Name',required=True)
    date_of_birth = fields.Date(string='Date of Birth',required=True)
    joining_date = fields.Date(string='Joining Date',required=True)
    designation = fields.Char(string='Designation')
    department_id = fields.Many2one('bsi.employee.department',string='Department')
    basic_salary = fields.Float(string='Basic Salary',required=True)
    employee_code = fields.Char(string='Employee Code',readonly=True,copy=False)

    status = fields.Selection(
        [
            ('probation', 'Probation'),
            ('confirmed', 'Confirmed'),
            ('resigned', 'Resigned'),
        ],
        string='Status',
        required=True,
        default='probation'
    )

    annual_salary = fields.Float(string='Annual Salary',compute='_compute_salary',store=True)
    bonus = fields.Float(string='Bonus',compute='_compute_salary',store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('employee_code'):
                vals['employee_code'] = (self.env['ir.sequence'].next_by_code('bsi.employee.code'))
        return super().create(vals_list)

    def get_age(self):
        self.ensure_one()
        if not self.date_of_birth:
            return 0
        today = date.today()
        age = (today.year - self.date_of_birth.year)

        if (today.month,today.day) < (self.date_of_birth.month,self.date_of_birth.day):
            age -= 1

        return age

    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        if self.date_of_birth:
            age = self.get_age()
            if age < 18:
                return {
                    'warning': {
                        'title': 'Age Warning',
                        'message': ('Employee must be at least 18 years old.'),
                    }
                }

    @api.constrains('date_of_birth')
    def _check_age(self):
        for employee in self:
            if employee.date_of_birth:
                age = employee.get_age()
                if age < 18:
                    raise ValidationError('Employee must be at least 18 years old.')

    @api.constrains('basic_salary')
    def _check_basic_salary(self):
        for employee in self:
            if employee.basic_salary <= 0:
                raise ValidationError('Basic salary must be greater than 0.')

    @api.depends('basic_salary','joining_date')
    def _compute_salary(self):
        today = date.today()
        for employee in self:
            employee.annual_salary = (employee.basic_salary * 12)
            employee.bonus = 0
            if employee.joining_date:
                years = (today.year -employee.joining_date.year)
                if (today.month,today.day) < (employee.joining_date.month,employee.joining_date.day):
                    years -= 1

                if years >= 1:
                    employee.bonus = (employee.annual_salary * 10 / 100)

    def write(self, vals):
        if ('basic_salary' in vals and not self.env.context.get('allow_salary_revision')):
            for employee in self:
                if employee.status == 'confirmed':
                    raise ValidationError('Confirmed employee salary cannot be changed.')
        return super().write(vals)

    def unlink(self):
        for employee in self:
            if employee.status == 'confirmed':
                raise ValidationError('Confirmed employee cannot be deleted.')
        return super().unlink()

    def action_confirm(self):
        for employee in self:
            if employee.status != 'probation':
                raise ValidationError('Only probation employees can be confirmed.')
            employee.status = 'confirmed'
        return True

    def action_resign(self):
        for employee in self:
            if employee.status != 'confirmed':
                raise ValidationError('Only confirmed employees can be resigned.')
            employee.status = 'resigned'
        return True