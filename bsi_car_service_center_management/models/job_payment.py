from odoo import models, fields


class JobPayment(models.Model):
    _name = 'job.payment'
    _description = 'Payment received against a Job Card'

    job_id = fields.Many2one('job.card', required=True, ondelete='cascade')
    amount = fields.Float(required=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
    ], default='cash', required=True)
    payment_date = fields.Date(default=fields.Date.context_today)