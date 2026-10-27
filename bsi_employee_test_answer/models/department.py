from odoo import fields, models


class EmployeeDepartment(models.Model):
    _name = 'bsi.employee.department'
    _description = 'Employee Department'
 
    name = fields.Char(string='Department Name',required=True)
    manager_id = fields.Many2one('res.partner',string='Manager')
    employee_ids = fields.One2many('bsi.employee','department_id',string='Employees')
    employee_count = fields.Integer(string='Employee Count',compute='_compute_employee_count')

    def _compute_employee_count(self):
        for department in self:
            department.employee_count = len(department.employee_ids)

    def action_open_employees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employees',
            'res_model': 'bsi.employee',
            'view_mode': 'list,form',
            'domain': [('department_id', '=', self.id)],
            'context': {'default_department_id': self.id},
        }