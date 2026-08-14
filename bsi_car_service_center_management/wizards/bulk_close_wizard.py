from odoo import models, fields


class BulkCloseWizard(models.TransientModel):
    _name = 'bulk.close.wizard'
    _description = 'Create Invoices for Completed Jobs'

    job_ids = fields.Many2many('job.card', string='Jobs', readonly=True)

    def action_create_invoices(self):
        for job in self.job_ids:
            if job.invoice_generated:
                print('Invoice already exists for %s - replacing it.' % job.name)
            else:
                print('Creating a new invoice for %s.' % job.name)
            job.invoice_number = 'INV-%s' % job.name
            job.invoice_generated = True
            job.state = 'delivered'
        return {'type': 'ir.actions.act_window_close'}

    def action_notify_customers(self):
        for job in self.job_ids:
            print('Notified %s regarding job %s.' % (job.customer_id.name, job.name))
