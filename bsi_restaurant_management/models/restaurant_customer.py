from odoo import models,fields

class RestaurantCustomer(models.Model):
	_name = 'restaurant.customer'
	_description = 'Customer'

	name = fields.Char(required = True)
	mobile = fields.Char()
	email = fields.Char()
	address = fields.Text()

	is_regular = fields.Boolean(string = 'Regular Customer' , required = False)
	