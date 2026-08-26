from odoo import models,fields

class AccountMove(models.Model):
	_inherit = 'account.move'

	custom_name = fields.Char(string="Custom Name")
	

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	custom_weight = fields.Char(string="Custom Weight")
