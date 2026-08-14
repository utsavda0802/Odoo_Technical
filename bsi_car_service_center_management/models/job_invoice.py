from odoo import models, fields, api
from odoo.exceptions import UserError


class JobInvoice(models.Model):
	_name = 'job.invoice'
	_description = 'Job Invoice'

	name = fields.Char(string='Invoice Number', required=True, copy=False)
	job_id = fields.Many2one('job.card', string='Job Card', required=True, ondelete='cascade')
	customer_id = fields.Many2one('car.customer', required=True, string='Customer')
	vehicle_id = fields.Many2one('car.vehicle', required=True, string='Car')
	mechanic_id = fields.Many2one('car.mechanic', required=True)
	job_type_ids = fields.Many2many('job.type', string='Job Type')
	arrival_date = fields.Date(required=True, default=fields.Date.context_today)
	expected_delivery_date = fields.Date(required=True)
	is_priority = fields.Boolean(string='Rush/Priority Job')
	labor_charges = fields.Float(default=0.0)
	parts_total = fields.Float(compute='_compute_totals', store=True)
	discount_percent = fields.Float(string='Discount %', default=0.0)
	total = fields.Float(compute='_compute_totals', store=True)
	line_ids = fields.One2many('job.invoice.line', 'invoice_id', string='Spare Parts Used')

	state = fields.Selection([
	    ('new', 'New'),
	    ('posted', 'Posted'),
	], default='new')
	invoice_date = fields.Date(readonly=True)

	@api.depends('line_ids.subtotal', 'labor_charges', 'discount_percent')
	def _compute_totals(self):
	    for invoice in self:
	        invoice.parts_total = sum(invoice.line_ids.mapped('subtotal'))
	        subtotal = invoice.parts_total + invoice.labor_charges
	        discount_amount = subtotal * invoice.discount_percent / 100
	        invoice.total = subtotal - discount_amount
		
	def action_post(self):
		self.ensure_one()
		if self.state == 'posted':
			raise UserError("This invoice is already posted.")
		self.write({'state': 'posted',
			'invoice_date': fields.Date.context_today(self),})
		self.job_id.write({
			'state': 'delivered',
			'invoice_number': self.name,
			'invoice_generated': True,
			})
		return self.env.ref('bsi_car_service_center_management.action_report_job_invoice').report_action(self)

	_name_unique = models.Constraint(
	    'unique(name)',
	    'Invoice number must be unique.',
	)