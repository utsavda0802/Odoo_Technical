from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RestaurantOrder(models.Model):
    _name = 'restaurant.order'
    _description = 'Restaurant Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order_no = fields.Char(string='Order Number', required=True)
    customer_id = fields.Many2one('restaurant.customer', string='Customer')
    table_id = fields.Many2one('restaurant.table', string='Table')
    order_datetime = fields.Datetime(default=fields.Datetime.now)
    table_capacity = fields.Integer(string="Table Capacity",related="table_id.capacity",store=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('served', 'Served'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], default='draft')
    note = fields.Text()
    total_amount = fields.Float(string='Total Amount', compute="_compute_total_amount", store=True)
    order_line_ids = fields.One2many("restaurant.order.line", "order_id", string='Order Lines')

    @api.depends("order_line_ids.subtotal")
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(order.order_line_ids.mapped("subtotal"))

    def action_calculate_total(self):
        for order in self:
            order.total_amount = sum(order.order_line_ids.mapped("subtotal"))

    @api.onchange("table_id")
    def _onchange_table(self):
        if self.table_id:
            self.note = (self.note or "") + "\nTable capacity: %s" % self.table_id.capacity

    @api.constrains("customer_id")
    def _check_customer_mobile(self):
        for rec in self:
            if rec.customer_id and not rec.customer_id.mobile:
                raise ValidationError("Customer must have a phone number.")

    @api.onchange("table_id")
    def _onchange_table_status(self):
        if self.table_id and not self.table_id.is_available:
            return {
                'warning': {
                    'title': "Table Occupied",
                    'message': "This table is currently marked unavailable. Please confirm before proceeding."
                }
            }
