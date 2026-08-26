from odoo import models,fields

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	custom_name= fields.Char(string='Custom Name')

	def _prepare_invoice(self):
		invoice_vals = super()._prepare_invoice()
		invoice_vals['custom_name'] = self.custom_name
		return invoice_vals


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	custom_weight = fields.Float(string = 'Custom Weight')

	def _prepare_invoice_line(self,**optional_values):
		vals = super()._prepare_invoice_line(**optional_values)
		vals['custom_weight'] = self.custom_weight
		return vals