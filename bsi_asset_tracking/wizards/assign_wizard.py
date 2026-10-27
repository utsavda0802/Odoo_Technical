from odoo import api,fields,models
from odoo.exceptions import UserError

class AssetAssignWizard(models.TransientModel):
    _name = 'asset.assign.wizard'
    _description = 'Asset Assign Wizard'

    employee_id = fields.Many2one('hr.employee',string='EMPLOYEE',required=True)
    location = fields.Selection([('office','Office'),('warehouse','Warehouse'),('remote','Remote'),('in_repair','In Repair')],default='office',tracking=True)
    asset_ids = fields.Many2many('asset.asset',string='Assets',required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        res['asset_ids'] = [(6, 0, active_ids)]
        return res

    def action_assign(self):
        if not self.asset_ids:
            raise UserError("Select atleast one asset.")
        assigned = 0
        skipped = 0
        for asset in self.asset_ids:
            if asset.condition =='disposed':
                skipped += 1
            else:
                asset.write({'employee_id':self.employee_id.id,'location':self.location})
                assigned += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Assignment Done',
                'message': "Assigned : %d, Skipped(disposed) : %d" % (assigned, skipped),
                'type': 'success',
                'sticky': False,
                'next':{'type':'ir.actions.act_window_close'},
            }
        }
