from odoo import models,fields

class Teacher(models.Model):
    _name = 'bsi.teacher'
    _description = 'Teacher'

    name = fields.Char(string='Name', required=True)
    