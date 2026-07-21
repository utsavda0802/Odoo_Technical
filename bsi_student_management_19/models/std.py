from odoo import models,fields

class Standard(models.Model):
    _name = 'bsi.std'
    _description = 'Standard'

    name = fields.Char(string='Name', required=True)
    teacher_count = fields.Integer(string="Teacher Count")
    student_ids = fields.One2many("bsi.student", "std_id", string="Students")
