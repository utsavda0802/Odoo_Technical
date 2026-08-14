from odoo import models,fields,api

class CarMechanic(models.Model):

	_name='car.mechanic'
	_description = 'Service Mechanic'

	name = fields.Char(required=True)
	on_leave = fields.Boolean(string="On Leave")
	job_ids = fields.One2many('job.card','mechanic_id')

	# req:-3 used to block assigning overload mechanics

	active_job_count = fields.Integer(compute = '_compute_active_job_count',store=True) 

	@api.depends('job_ids.state')
	def _compute_active_job_count(self):
		for rec in self:
			rec.active_job_count = len(rec.job_ids.filtered(lambda j: j.state not in ('completed','delivered')))