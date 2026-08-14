from odoo import models,fields,api

class JobInvoiceline(models.Model):
	_name = 'job.invoice.line'
	_description = 'Job Invoice Line'

	invoice_id = fields.Many2one('job.invoice', required=True, ondelete='cascade')
	part_id = fields.Many2one('spare.part',required=True,string='Spare Parts')
	quantity = fields.Float(default=1.0)
	unit_price = fields.Float()
	subtotal = fields.Float(compute='_compute_subtotal',store=True)

	@api.onchange('part_id')
	def _onchange_part_id(self):
		if self.part_id:
			self.unit_price = self.part_id.unit_price

	@api.depends('quantity','unit_price')
	def _compute_subtotal(self):
		for rec in self:
			rec.subtotal = rec.quantity*rec.unit_price
