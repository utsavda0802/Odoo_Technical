from odoo import models,fields

class RestaurantTag(models.Model):
	_name = 'restaurant.tag'
	_description = 'Food Tags'


	name = fields.Char(required = True)