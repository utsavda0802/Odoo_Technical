from odoo import models, fields, api


class RentalReturnWizard(models.TransientModel):
    _name = 'rental.return.wizard'
    _description = 'Return Equipment Wizard'

    rental_id = fields.Many2one('rental.order', string='Rental Order', required=True)
    return_date = fields.Date(string='Return Date', default=fields.Date.today, required=True)
    condition = fields.Selection([
        ('good', 'Good'),
        ('damaged', 'Damaged'),
    ], string='Condition', default='good', required=True)
    damage_note = fields.Text(string='Damage Note')

    def action_confirm_return(self):
        self.ensure_one()
        order = self.rental_id

        order.write({
            'state': 'returned',
            'actual_return_date': self.return_date,
            'return_condition': self.condition,
            'damage_note': self.damage_note,
        })

        for line in order.line_ids:
            line.equipment_id.status = 'available'

        return {'type': 'ir.actions.act_window_close'}