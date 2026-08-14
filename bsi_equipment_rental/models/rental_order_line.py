from odoo import models,fields,api
from odoo.exceptions import ValidationError

class RentalOrderLine(models.Model):

	_name='rental.order.line'
	_description= 'Rental Order Line'

	rental_id = fields.Many2one('rental.order',string='Rental Order',ondelete='cascade')
	equipment_id = fields.Many2one('rental.equipment',string='Equipment')
	quantity = fields.Integer(string='Quantity',default=1)
	price_per_day = fields.Float(string='Price per Day')
	days = fields.Integer(string='Days',default=1)
	amount = fields.Float(string='Amount',compute='_compute_amount',store=True)

	@api.depends('quantity','price_per_day','days')
	def _compute_amount(self):
		for line in self :
			line.amount = line.quantity*line.price_per_day*line.days
			
	@api.onchange('equipment_id')
	def _onchange_equipment_id(self):
	    if self.equipment_id:
	        self.price_per_day = self.equipment_id.price_per_day
	        if self.equipment_id.status != 'available':
	            return {
	                'warning': {
	                    'title': "Equipment Not Available",
	                    'message': f"{self.equipment_id.name} is currently '{self.equipment_id.status}'. Please pick a different item."
	                }
	            }

	@api.constrains('equipment_id')
	def _check_equipment_available(self):
	    for line in self:
	        if line.equipment_id and line.equipment_id.status != 'available':
	            raise ValidationError(
	                f"Cannot use '{line.equipment_id.name}' — it is currently '{line.equipment_id.status}', not Available."
	            )