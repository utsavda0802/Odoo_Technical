from odoo import models, fields, api
from odoo.exceptions import ValidationError


class JobPaymentWizard(models.TransientModel):
    _name = 'job.payment.wizard'
    _description = 'Register a Payment against a Job Card'

    job_id = fields.Many2one('job.card', required=True, readonly=True)

    # related = read this value live from job.card, don't store it here
    total_amount = fields.Float(related='job_id.total_amount', readonly=True)
    advance_paid = fields.Float(related='job_id.advance_paid', readonly=True)
    balance_due = fields.Float(related='job_id.balance_due', readonly=True)

    amount = fields.Float(string='Amount to Pay', required=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
    ], default='cash', required=True)

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Payment amount must be greater than zero.")
            if rec.amount > rec.balance_due:
                raise ValidationError(
                    "Payment amount cannot be more than the balance due (%.2f)." % rec.balance_due
                )

    def action_confirm_payment(self):
        self.ensure_one()
        self.env['job.payment'].create({
            'job_id': self.job_id.id,
            'amount': self.amount,
            'payment_method': self.payment_method,
        })
        print('Received %.2f (%s) for job %s.' % (self.amount, self.payment_method, self.job_id.name))
        return {'type': 'ir.actions.act_window_close'}