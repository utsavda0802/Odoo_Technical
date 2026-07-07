from odoo import models,fields

class RestaurantTable(models.Model) :
	_name = 'restaurant.table'
	_description = 'Restaurant Table'

	name = fields.Char(string = 'Table Number' , required = True)
	capacity = fields.Integer(string = 'Capacity' , required = True)
	is_available = fields.Boolean(string = 'Available' ,default = 'True')