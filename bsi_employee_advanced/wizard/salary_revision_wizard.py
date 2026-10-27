from odoo import api,fields,models
from odoo.exceptions import UserError

class SalaryRevisionWizard(models.TransientModel):

    _name = 'test.salary.revision.wizard'
    _description = 'Salary Revision Wizard'

    percentage = fields.Float(required=True)
    employee_ids = fields.Many2many('test.employee',string="Employee")

    @api.model
    def default_get(self,fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids',[])
        res['employee_ids'] = [(6,0,active_ids)]
        return res

    def action_apply(self):
        if not self.employee_ids:
            raise UserError("Please select atleast one employee.")
        if self.percentage <= -100:
            raise UserError("percentage must be > than -100.")
        
        updated = 0
        skipped = 0

        for emp in self.employee_ids:
            if emp.status == 'confirmed':
                emp.salary = emp.salary + emp.salary * self.percentage / 100
                updated += 1
            else:
                skipped += 1

        return {
            'type' : 'ir.actions.client',
            'tag' : 'display_notification',
            'params' : {
                'title' : 'Salary revision Done.',
                'message' : "Updated Employees : %d , Skipped Employees : %d" %(updated,skipped),
                'type' : 'success',
                'sticky' : True,
                'next' : {'type' : 'ir.actions.act_window_close'},
            },
        }