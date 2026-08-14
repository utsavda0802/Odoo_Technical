from odoo import models, fields, api

class CarVehicle(models.Model):
    _name = 'car.vehicle'
    _description = 'Customer Vehicle'

    name = fields.Char(compute='_compute_name', store=True)

    customer_id = fields.Many2one('car.customer', required=True, string='Owner')
    make = fields.Char(required=True)
    model = fields.Char(required=True)
    license_plate = fields.Char(required=True)
    year = fields.Char()

    job_ids = fields.One2many('job.card', 'vehicle_id', string='Service History')
    job_count = fields.Integer(compute='_compute_job_count')

    _plate_unique = models.Constraint(
        'unique(license_plate)',
        'This license plate is already registered.'
    )

    @api.depends('make', 'model', 'license_plate')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.make} {rec.model} ({rec.license_plate})"

    @api.depends('job_ids')
    def _compute_job_count(self):
        for rec in self:
            rec.job_count = len(rec.job_ids)

    def action_view_jobs(self):
	    self.ensure_one()
	    return {
	        'name': 'Service History',
	        'type': 'ir.actions.act_window',
	        'res_model': 'job.card',
	        'view_mode': 'list,form',
	        'domain': [('id', 'in', self.job_ids.ids)],
	    }