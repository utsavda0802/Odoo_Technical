from odoo import api,fields, models


class TestDepartment(models.Model):
    _name = 'test.department'
    _description = 'Department'

    name = fields.Char(required=True)
    code = fields.Char()
    manager_id = fields.Many2one('res.users', string='Manager')
    employee_ids = fields.One2many('test.employee', 'department_id', string='Employees')
    yearly_salary_total = fields.Float(string = 'Yearly Salary Total' , compute = '_compute_yearly_salary_total',store = True)

    @api.depends('employee_ids.salary','employee_ids.status','employee_ids.active','employee_ids.department_id')
    def _compute_yearly_salary_total(self):
        for dept in self:
            total = 0
            for emp in dept.employee_ids:
                if emp.active and emp.status == 'confirmed' :
                    total = total + emp.salary
            dept.yearly_salary_total = total * 12