from odoo import models,fields

class RestaurantCataegory(models.Model):
	_name = 'restaurant.category'
	_description ='Food Category'

	name = fields.Char(required = True)
	description = fields.Text()
