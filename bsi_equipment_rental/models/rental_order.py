from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RentalOrder(models.Model):
    _name = 'rental.order'
    _description = 'Equipment Rental Order'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string='Rental Reference', default='New', copy=False)

    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True,
        domain="[('is_rental_customer', '=', True)]"
    )

    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    rental_days = fields.Integer(string='Rental Days', default=1)
    return_date = fields.Date(
        string='Expected Return Date', compute='_compute_return_date',
        store=True, readonly=False
    )

    line_ids = fields.One2many('rental.order.line', 'rental_id', string='Rental Lines')

    discount = fields.Float(string='Discount (%)', default=0.0)

    express_charge = fields.Float(
        string='Express Charge (10%)', compute='_compute_total_amount', store=True
    )

    total_amount = fields.Float(
        string='Total Amount', compute='_compute_total_amount',
        store=True, aggregator='sum'
    )

    urgent_delivery = fields.Boolean(string='Urgent Delivery')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('line_ids.amount', 'discount', 'urgent_delivery')
    def _compute_total_amount(self):
        for rec in self:
            subtotal = sum(rec.line_ids.mapped('amount'))
            after_discount = subtotal - (subtotal * rec.discount / 100)
            rec.express_charge = after_discount * 0.10 if rec.urgent_delivery else 0.0
            rec.total_amount = after_discount + rec.express_charge

    @api.depends('start_date', 'rental_days')
    def _compute_return_date(self):
        for rec in self:
            if rec.start_date and rec.rental_days:
                rec.return_date = rec.start_date + timedelta(days=rec.rental_days)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.email = self.partner_id.email

    @api.onchange('return_date')
    def _onchange_return_date(self):
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.order') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError("Cannot confirm a rental with zero lines.")

            rec.state = 'confirmed'

            for line in rec.line_ids:
                line.equipment_id.status = 'rented'

            for line in rec.line_ids:
                self.env['rental.handover'].sudo().create({
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

    def action_cancel(self):
        self.write({'state': 'cancelled'})

