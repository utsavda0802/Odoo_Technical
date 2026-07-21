from odoo import models, fields

class RentalHandover(models.Model):
    _name = 'rental.handover'
    _description = 'Equipment Handover Record'

    rental_id = fields.Many2one('rental.order', string='Rental Order', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    equipment_id = fields.Many2one('rental.equipment', string='Equipment', required=True)
    handover_date = fields.Date(string='Handover Date', default=fields.Date.today)
    notes = fields.Text(string='Notes')