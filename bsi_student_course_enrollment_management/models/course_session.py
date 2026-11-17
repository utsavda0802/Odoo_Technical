from odoo import models, fields

class TrainingCourseSession(models.Model):
    _name = 'training.course.session'
    _description = 'Training Course Session'

    name = fields.Char(string='Session Name', required=True)
    course_id = fields.Many2one('training.course', string='Course', required=True, ondelete='cascade')
    session_date = fields.Date(string='Session Date', required=True)
    instructor = fields.Char(string='Instructor')