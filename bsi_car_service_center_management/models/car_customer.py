from odoo import models,fields

class CarCustomer(models.Model):

	_name = 'car.customer'
	_description = 'Car Service Customer'

	name = fields.Char(required=True)
	phone = fields.Char(required=True)
	email = fields.Char()

	vehicle_ids = fields.One2many('car.vehicle','customer_id',string='Vehicles')

	_sql_constraints = [('phone_unique','unique(phone)', 'A customer with this phone number already exists'),]