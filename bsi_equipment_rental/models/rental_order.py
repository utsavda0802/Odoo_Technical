from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RentalOrder(models.Model):
    _name = 'rental.order'
    _description = 'Rental Order'
    _inherit = ['mail.thread']

    name = fields.Char(string='Rental Reference')
    partner_id = fields.Many2one('rental.customer', string='Customer', ondelete='restrict')
    phone = fields.Char(string="Customer Mobile No.")
    email = fields.Char(string="Customer Email Id")

    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    rental_days = fields.Integer(string='Rental Days', default=1)
    return_date = fields.Date(string='Return Date', compute='_compute_return_date', store=True, readonly=False)

    line_ids = fields.One2many('rental.order.line', 'rental_id', string='Rental Lines')

    discount = fields.Float(string='Discount (%)', default=0.0)
    urgent_delivery = fields.Boolean(string='Urgent Delivery')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
    ], string='Status', default='draft', tracking=True)


    # Wizards

    actual_return_date = fields.Date(string='Actual Return Date')
    return_condition = fields.Selection([
        ('good', 'Good'),
        ('damaged', 'Damaged'),
    ], string='Return Condition')
    damage_note = fields.Text(string='Damage Note')

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.email = self.partner_id.email
            if not self.partner_id.is_customer:
                return {
                    'warning': {
                        'title': "Not a Customer",
                        'message': f"{self.partner_id.name} is not marked as a customer."
                    }
                }
        else:
            self.phone = False
            self.email = False

    @api.constrains('partner_id')
    def _check_partner_is_customer(self):
        for rec in self:
            if rec.partner_id and not rec.partner_id.is_customer:
                raise ValidationError(
                    f"Cannot create a rental for '{rec.partner_id.name}' — this contact is not marked as a customer."
                )

    @api.onchange("phone", "email")
    def _onchange_update_customer(self):
        if self.partner_id:
            self.partner_id.write({
                "phone": self.phone,
                "email": self.email,
            })

    @api.depends('line_ids.amount', 'discount', 'urgent_delivery')
    def _compute_total_amount(self):
        for rec in self:
            subtotal = sum(rec.line_ids.mapped('amount'))
            after_discount = subtotal - (subtotal * rec.discount / 100)
            if rec.urgent_delivery:
                after_discount += after_discount * 0.10
            rec.total_amount = after_discount

    @api.depends('start_date', 'rental_days')
    def _compute_return_date(self):
        for rec in self:
            if rec.start_date and rec.rental_days:
                rec.return_date = rec.start_date + timedelta(days=rec.rental_days)

    @api.onchange('return_date')
    def _onchange_return_date(self):
        print('rental_days')
        if self.start_date and self.return_date:
            delta = (self.return_date - self.start_date).days
            if delta >= 0 and delta != self.rental_days:
                self.rental_days = delta

    @api.onchange('urgent_delivery')
    def _onchange_urgent_delivery(self):
        if self.urgent_delivery:
            return {
                'warning': {
                    'title': "Express Charge Notice",
                    'message': "Urgent Delivery adds a 10% express charge to this rental."
                }
            }

    @api.constrains('discount')
    def _check_discount(self):
        for rec in self:
            if not (0 <= rec.discount <= 100):
                raise ValidationError("Discount must be between 0 and 100.")

    @api.constrains('start_date', 'return_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.return_date and rec.return_date < rec.start_date:
                raise ValidationError("Return date cannot be before the start date.")

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError("Cannot confirm a rental with zero lines.")
            rec.state = 'confirmed'
            for line in rec.line_ids:
                line.equipment_id.status = 'rented'
                self.env['rental.handover'].create({
                    'rental_id': rec.id,
                    'partner_id': rec.partner_id.id,
                    'equipment_id': line.equipment_id.id,
                    'handover_date': fields.Date.today(),
                })

    def action_mark_returned(self):
        for rec in self:
            rec.state = 'returned'
            for line in rec.line_ids:
                line.equipment_id.status = 'available'

    def action_open_return_wizard(self):
        self.ensure_one()
        return {
            'name': 'Return Equipment',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.return.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_rental_id': self.id},
        }