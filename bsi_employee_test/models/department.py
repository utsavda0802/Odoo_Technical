from odoo import models,fields,api

class Department(models.Model):

	_name='department'
	_description = 'Department'

	emp_id = fields.Many2one('employee',string='Employee')