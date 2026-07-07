from odoo import models,fields

class Student(models.Model):
    _name = 'bsi.student'
    _description = 'Student'

    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', required=True)
    enrollment_no = fields.Text(string= 'Enrollment no.', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone', required=True)
    joining_date = fields.Date(string='Joining Date', default=fields.Date.context_today, required=True)
    fees = fields.Float(string= 'Fees')
    active = fields.Boolean(string='Active', default=True, required=True)

    std_id = fields.Many2one("bsi.std", string="Standard")
    teacher_ids = fields.Many2many("bsi.teacher", string="Teachers")
