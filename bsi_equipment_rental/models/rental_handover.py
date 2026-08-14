from odoo import models,fields

class RentalHandover(models.Model):
	_name = 'rental.handover'
	_description = 'Equipment Handover Record'

	rental_id = fields.Many2one('rental.order',string='Rental Order',ondelete='cascade')
	partner_id = fields.Many2one('rental.customer',string='Customer',ondelete='restrict')
	equipment_id = fields.Many2one('rental.equipment',string='Equipment')
	handover_date = fields.Date(string='Handover Date', default=fields.Date.today)
	notes = fields.Text(string='Notes')
