from odoo import models, fields


class Course(models.Model):
    _name = 'bsi.course'
    _description = 'Course'

    name = fields.Char(string='Course Name', required=True)
    duration = fields.Char(string='Duration')
    fees = fields.Float(string='Fees')
    student_ids = fields.One2many('bsi.student', 'course_id', string='Students')