from odoo import models,fields

class JobType(models.Model):
	_name = 'job.type'
	_description = 'Job Type Tag(Repair,Maintenance,Accident,Insurance,etc...)'

	name = fields.Char(required=True)