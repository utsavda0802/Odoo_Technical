from odoo import models,fields,api
from odoo.exceptions import ValidationError


    
class Employee(models.Model):
	_name='employee'
	_description = 'Employee'

	name = fields.Char(required = True)
    date_of_birth = fields.Date(default=fields.Date.context_today, required=True)
    joining_date = fields.Date(string ='Joining Date',default=fields.Date.context_today)
    designation = fields.Char(string='Designation')
    department = fields.One2many('department','emp_id',string='Department')
    basic_salary = fields.Float(string='Basic Salary')
    employee_code = fields.Char(string='Employee Code')

    status = fields.Selection([
        ('probation', 'Probation'),
        ('confirmed', 'Confirmed'),
        ('resigned', 'Resigned'),
    ], string='Status', default='probation', tracking=True)

    annual_salary = fields.Float(string='Annual Salary', compute='_compute_annual_salary',store=True)
    bonus = fields.Float(string='Bonus', compute='_compute_bonus',store=True,default=0)

    @api.constrains('basic_salary')
    def _check_basic_salary(self):
        for rec in self:
            if rec.basic_salary <= 0:
                raise ValidationError('Basic Salary must be at greater than 0.')

    @api.depends('basic_salary')
	def _compute_annual_salary(self):
		for rec in self:
			rec.annual_salary = rec.basic_salary*12

	@api.depends('basic_salary')
	def _compute_bonus(self):
		for rec in self:
			rec.bonus = rec.annual_salary*10/100

	@api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_code', 'New') == 'New':
                vals['employee_code'] = self.env['ir.sequence'].next_by_code('bsi.employee') or 'New'
        return super().create(vals_list)

    _employee_code_unique = models.Constraint(
        'UNIQUE(employee_code)',
        'Employee ID must be unique!',
    )

    def status_salary(self):
    	for emp in self:
    		if emp.status == 'confirmed':
    			raise UserError(_("Once the employee's is confirmed his basic salary can not be editable"))

    @api.onchange('date_of_birth')
    def _onchange_dateofbirth(self):
    	if self.date_of_birth:
    		return {
                'warning': {
                    'title': "Age Limit Crieteria",
                    'message': "Employee's age must be greater than 18."
                }
            }