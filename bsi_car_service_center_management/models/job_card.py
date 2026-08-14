from odoo import models,fields,api
from odoo.exceptions import ValidationError, UserError

class JobCard (models.Model):

	_name = 'job.card'
	_description = 'Service Job Card'

	name = fields.Char(default='New',copy=False,readonly=True)

	# req:-1 customer + car

	customer_id = fields.Many2one('car.customer',required=True,string='Customer')
	vehicle_id = fields.Many2one('car.vehicle',required=True,string='Car')

	# req:-2 job card fields

	arrival_date = fields.Date(required=True,default=fields.Date.context_today)
	expected_delivery_date = fields.Date(required=True)
	mechanic_id = fields.Many2one('car.mechanic',required=True)
	problem_description=fields.Text(string="Problem Description")
	is_priority = fields.Boolean(string='Rush/Priority Job')
	job_type_ids = fields.Many2many('job.type',string='Job Type')
	photo_ids = fields.Many2many('ir.attachment',string='Arrival Photos')

	# req:-6 status

	state = fields.Selection([
	    ('new','New'),
	    ('in_progress','In Progress'),
	    ('waiting_parts','Waiting for Parts'),
	    ('completed','Completed'),
	    ('delivered','Delivered'),
	], default='new')

	# req:-4 parts and labor

	part_line_ids = fields.One2many('job.card.part.line','job_id',string='Spare Parts Used')
	labor_charges = fields.Float(default=0.0)
	parts_total = fields.Float(compute='_compute_totals',store=True)
	discount_percent = fields.Float(string='Discount %',default=0.0)
	total_amount = fields.Float(compute='_compute_totals',store=True)

	# req:-5 payments
	payment_ids = fields.One2many('job.payment', 'job_id', string='Payments')
	advance_paid = fields.Float(compute='_compute_advance_paid', store=True)
	balance_due = fields.Float(compute='_compute_totals',store=True)

	@api.depends('payment_ids.amount')
	def _compute_advance_paid(self):
		for rec in self:
			rec.advance_paid = sum(rec.payment_ids.mapped('amount'))

	# req:-7 bulk closing / invoicing
	invoice_number = fields.Char(string='Invoice Number', readonly=True, copy=False)
	invoice_generated = fields.Boolean(string='Invoice Generated', default=False, copy=False)
	invoice_ids = fields.One2many('job.invoice','job_id',string='Invoices')

	@api.depends('part_line_ids.subtotal','labor_charges','discount_percent','advance_paid')
	def _compute_totals(self):
		for rec in self:
			rec.parts_total = sum(rec.part_line_ids.mapped('subtotal'))
			subtotal = rec.parts_total + rec.labor_charges
			discount_amount = subtotal * (rec.discount_percent / 100)
			rec.total_amount = subtotal - discount_amount
			rec.balance_due = rec.total_amount - rec.advance_paid
			
	# req:-1 dates cant be nonsensical
	@api.constrains('arrival_date','expected_delivery_date')
	def _check_dates(self):
		for rec in self:
			if rec.expected_delivery_date and rec.arrival_date and rec.expected_delivery_date < rec.arrival_date:
				raise ValidationError("Expected delivery date connot be before the arrival date")

	# req:-1 the car must belong to the chosen customer
	@api.constrains('vehicle_id','customer_id')
	def _check_vehicle_belongs_to_customer(self):
		for rec in self:
			if rec.vehicle_id and rec.customer_id and rec.vehicle_id.customer_id != rec.customer_id:
				raise ValidationError("The selected car does not belong to the selected customer")

	@api.onchange('customer_id')
	def _onchange_customer_id(self):
		if self.vehicle_id and self.customer_id and self.vehicle_id.customer_id != self.customer_id:
			self.vehicle_id = False


	#  req:-3 mechanic must be free
	@api.constrains('mechanic_id', 'state')
	def _check_mechanic_availability(self):
		for rec in self:
			if rec.mechanic_id and rec.state not in ('completed','delivered'):
				if rec.mechanic_id.on_leave:
					raise ValidationError("%s is on leave and cannot be assigned" % rec.mechanic_id.name)
				active_jobs = self.env['job.card'].search_count([
					('mechanic_id','=',rec.mechanic_id.id),
					('state','not in',['completed','delivered']),
					('id', '!=', rec.id),])
				if active_jobs >= 3:
					raise ValidationError("%s already has 3 or more active jobs." %rec.mechanic_id.name)

	@api.onchange('mechanic_id')
	def _onchange_mechanic_id(self):
		if self.mechanic_id:
			if self.mechanic_id.on_leave:
				return {'warning':{
				'title': 'Not available',
				'message' : '%s is on leave.' % self.mechanic_id.name,
				}}
			active_jobs = self.env['job.card'].search_count([
				('mechanic_id','=',self.mechanic_id.id),
				('state','not in',['completed','delivered']),
				])
			if active_jobs >=3:
				return {'warning':{
				'title': 'Overloaded',
				'message' : '%s already has 3 or more active jobs.' % self.mechanic_id.name,
				}}

	# req:-6 buttons to move across the kanban board
	def action_set_in_progress(self):
		self.write({'state':'in_progress'})

	def action_set_waiting_parts(self):
		self.write({'state':'waiting_parts'})

	def action_set_completed(self):
		self.write({'state':'completed'})

	def action_set_delivered(self):
		self.write({'state':'delivered'})

	# practice wizard: opens the Register Payment popup
	def action_open_payment_wizard(self):
		self.ensure_one()
		if self.balance_due <= 0:
			raise UserError("This job has no balance due.")
		return {
			'name': 'Register Payment',
			'type': 'ir.actions.act_window',
			'res_model': 'job.payment.wizard',
			'view_mode': 'form',
			'target': 'new',
			'context': {'default_job_id': self.id},
		}

	# req:-7 header button on the list view - only enabled when rows are selected.
	# self here IS the selected job cards (like the Sales "Create Invoices" flow).
	def action_open_bulk_close_wizard(self):
		invalid = self.filtered(lambda j: j.state not in ('completed', 'delivered'))
		if invalid:
			raise UserError(
				"Only jobs with status Completed or Delivered can be invoiced.\n"
				"Please deselect: %s" % ', '.join(invalid.mapped('name'))
			)
		return {
			'name': 'Create Invoices',
			'type': 'ir.actions.act_window',
			'res_model': 'bulk.close.wizard',
			'view_mode': 'form',
			'target': 'new',
			'context': {'default_job_ids': [(6, 0, self.ids)]},
		}


	def action_create_invoice(self):
		self.ensure_one()
		line_commands=[(0,0,{
			'part_id':line.part_id.id,
			'quantity':line.quantity,
			'unit_price':line.unit_price,
			})for line in self.part_line_ids]
		return{
		'name': 'Create Invoice',
		'type' :'ir.actions.act_window',
		'res_model' :'job.invoice',
		'view_mode': 'form',
		'target': 'current',
		'context': {
			'default_job_id': self.id,
			'default_customer_id':self.customer_id.id,
			'default_vehicle_id':self.vehicle_id.id,
			'default_mechanic_id':self.mechanic_id.id,
			'default_job_type_ids':[(6,0,self.job_type_ids.ids)] ,
			'default_arrival_date':self.arrival_date,
			'default_expected_delivery_date':self.expected_delivery_date,
			'default_is_priority':self.is_priority,
			'default_labor_charges':self.labor_charges,
			'default_discount_percent':self.discount_percent,
			'default_line_ids':line_commands,
			},
		}