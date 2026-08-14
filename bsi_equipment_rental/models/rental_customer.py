from odoo import models, fields,api

class RentalCustomer(models.Model):
    _name = "rental.customer"
    _description = "Rental Customer"

    name = fields.Char(required=True)
    phone = fields.Char(string="Customer Mobile No.")
    email = fields.Char(string="Customer Email Id")
    is_customer = fields.Boolean(string="Is Customer", default=True)

    @api.depends('rental_ids')
    def _compute_rental_count(self):
        for rec in self:
            rec.rental_count = len(rec.rental_ids)

    def action_view_rentals(self):
        self.ensure_one()
        return {
            'name': 'Rentals',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
        }