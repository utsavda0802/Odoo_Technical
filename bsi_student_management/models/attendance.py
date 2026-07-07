from odoo import models, fields


class Attendance(models.Model):
    _name = 'bsi.attendance'
    _description = 'Attendance'

    student_id = fields.Many2one('bsi.student', string='Student', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ], string='Status', required=True, default='present')