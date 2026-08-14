from odoo import models,fields,api
from odoo.exceptions import ValidationError

class JobCardPartLine(models.Model):
	_name = 'job.card.part.line'
	_description = 'Spare Part used on a Job Card'

	job_id = fields.Many2one('job.card',required=True,ondelete='cascade')
	part_id = fields.Many2one('spare.part',required=True,string='Spare Part')
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


	# req:-4 block using more stock than what's availablke

	@api.constrains('quantity','part_id')
	def _check_stock(self):
		for rec in self:
			if rec.part_id and rec.quantity > rec.part_id.stock_qty:
				raise ValidationError("Not enough stock for '%s'. Available:%s,Requested:%s" % (rec.part_id.name,rec.part_id.stock_qty,rec.quantity))