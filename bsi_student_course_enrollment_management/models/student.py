from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TrainingStudent(models.Model):
    _name = 'training.student'
    _description = 'Training Student'

    name = fields.Char(string='Student Name', required=True)
    email = fields.Char(string='Email', required=True)
    age = fields.Integer(string='Age')
    course_ids = fields.Many2many(
        comodel_name='training.course',
        relation='training_course_student_rel',
        column1='student_id',
        column2='course_id',
        string='Enrolled Courses',
    )
    status = fields.Selection(
        [('new', 'New'), ('active', 'Active'), ('inactive', 'Inactive')],
        string='Status', default='new',
    )

    _sql_constraints = [('email_unique', 'unique(email)', 'A student with this email already exists.'),]

    @api.constrains('email')
    def _check_email_format(self):
        for student in self:
            if student.email and '@' not in student.email:
                raise ValidationError("Please enter a valid email address.")