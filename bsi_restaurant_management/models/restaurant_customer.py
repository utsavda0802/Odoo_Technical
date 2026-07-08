from odoo import models,fields,api
from odoo.exceptions import ValidationError

class RestaurantCustomer(models.Model):
	_name = 'restaurant.customer'
	_description = 'Customer'

	name = fields.Char(required = True)
	mobile = fields.Char(string="Customer Mobile No.")
	email = fields.Char(string="Customer Email")
	address = fields.Text()

	is_regular = fields.Boolean(string = 'Regular Customer' , required = False)

	@api.constrains("mobile")
	def _check_unique_mobile(self):
	    for rec in self:
	        if rec.mobile:
	            duplicate = self.search([
	                ("mobile", "=", rec.mobile),
	                ("id", "!=", rec.id)
	            ])
	            if duplicate:
	                raise ValidationError("A customer with this mobile number already exists.")