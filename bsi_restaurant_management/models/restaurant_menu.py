from odoo import models,fields

class RestaurantMenu(models.Model):
	_name = 'restaurant.menu'
	_description = 'Menu Item'

	name = fields.Char(required = True)
	description = fields.Text()

	price = fields.Float(string = 'Price',required=True)

	is_available = fields.Boolean(string = 'Available' , default = True)

	category_id = fields.Many2one('restaurant.category' , string = 'Category')

	tag_ids = fields.Many2many('restaurant.tag' , string = 'Tags')
