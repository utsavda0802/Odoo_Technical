from odoo import models,fields

class SparePart(models.Model):
	_name = 'spare.part'
	_description = 'Spare Part / Inventory Item'

	name = fields.Char(required=True)
	stock_qty = fields.Float(string='Stock Quantity' ,default = 0.0)
	unit_price = fields.Float(string="Unit Price",required=True)