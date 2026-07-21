from odoo import models,fields, api
from odoo.exceptions import ValidationError

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
    # t_count = fields.Integer(related="std_id.teacher_count" ,string="Teacher Count")
    # t_count = fields.Integer(string="Teacher Count", compute="compute_t_count")
    t_count = fields.Integer(string="Teacher Count")

    @api.constrains('enrollment_no')
    def check_enrollment_no(self):
        for rec in self:
            if len(rec.enrollment_no) > 10:
                raise ValidationError("The Enrollment Number should be under 10 character")

    @api.onchange('teacher_ids')
    def compute_t_count(self):
        for rec in self:
            count = self.env['bsi.teacher'].search_count([])


            # count = 0
            # for record in rec.teacher_ids:
            #     count += 1
            # rec.t_count = count
            # rec.std_id.teacher_count = count

