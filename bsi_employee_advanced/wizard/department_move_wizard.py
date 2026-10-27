from odoo import api,fields,models
from odoo.exceptions import UserError

class DepartmentMoveWizard(models.TransientModel):

    _name = 'test.department.move.wizard'
    _description = 'Department Move Wizard'

    employee_ids = fields.Many2many('test.employee',string="Employees")
    department_input = fields.Char(string='Department Name or Code', required = True)

    @api.model
    def default_get(self,fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids',[])
        res['employee_ids'] = [(6,0,active_ids)]
        return res

    def action_move(self):
        if not self.employee_ids:
            raise UserError("Select atlest one employee")

        text = self.department_input.strip()
        department = self.env['test.department'].search(['|', ('name', '=ilike', text), ('code', '=ilike', text)], limit=1)

        if not department:
            department = self.env['test.department'].create({'name':text})

        self.employee_ids.write({'department_id': department.id})

        return {
            'type' : 'ir.actions.client',
            'tag' : 'display_notification',
            'params' : {
                'title' : 'Employee Moved',
                'message' : "%d employees moved to %s department." % (len(self.employee_ids),department.name),
                'type' : 'success',
                'sticky' : True,
                'next' : {'type' : 'ir.actions.act_window_close'},
            },
        }