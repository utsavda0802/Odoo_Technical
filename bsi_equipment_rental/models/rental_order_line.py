from odoo import models, fields, api

class RentalOrderLine(models.Model):
    _name = 'rental.order.line'
    _description = 'Rental Order Line'

    # Req 10: cascade delete — deleting the order deletes its lines
    rental_id = fields.Many2one('rental.order', string='Rental Order',required=True, ondelete='cascade')

    # Req 2: only equipment currently "Available" should appear.
    # domain is set here as a default; the order also passes a dynamic
    # domain from the view so equipment already used on other DRAFT
    # lines within the same order doesn't double-book.
    equipment_id = fields.Many2one('rental.equipment', string='Equipment', required=True,domain="[('status', '=', 'available')]")

    quantity = fields.Integer(string='Quantity', default=1)
    price_per_day = fields.Float(string='Price per Day (₹)')
    days = fields.Integer(string='Days', related='rental_id.rental_days', store=True, readonly=True)

    amount = fields.Float(
        string='Line Amount', compute='_compute_amount', store=True)

    # ---------- Req 5: line amount auto-calculated, never typed ----------
    @api.depends('quantity', 'price_per_day', 'days')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_per_day * line.days

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id:
            self.price_per_day = self.equipment_id.price_per_day