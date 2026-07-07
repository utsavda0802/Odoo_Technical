from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Student(models.Model):
    _name = 'bsi.student'
    _description = 'Student'

    _student_code_unique = models.Constraint(
        'UNIQUE(student_code)',
        'Student ID must be unique!',
    )

    student_code = fields.Char(string='Student ID', required=True, copy=False,
                                readonly=True, default='New')
    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    joining_date = fields.Date(string='Joining Date', default=fields.Date.context_today)
    active = fields.Boolean(string='Active', default=True)

    course_id = fields.Many2one('bsi.course', string='Course')
    subject_ids = fields.Many2many('bsi.subject', string='Subjects')
    attendance_ids = fields.One2many('bsi.attendance', 'student_id', string='Attendance Records')

    attendance_count = fields.Integer(string='Attendance Count', compute='_compute_attendance_count')

    @api.depends('attendance_ids')
    def _compute_attendance_count(self):
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids)

    @api.constrains('age')
    def _check_age(self):
        for rec in self:
            if rec.age and rec.age < 5:
                raise ValidationError('Student age must be at least 5 years.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('student_code', 'New') == 'New':
                vals['student_code'] = self.env['ir.sequence'].next_by_code('bsi.student') or 'New'
        return super().create(vals_list)