from odoo import models, fields


class Subject(models.Model):
    _name = 'bsi.subject'
    _description = 'Subject'

    name = fields.Char(string='Subject Name', required=True)
    code = fields.Char(string='Subject Code', required=True)
    student_ids = fields.Many2many('bsi.student', string='Students')