from odoo import models, fields

class RestaurantOrder(models.Model):
    _name = 'restaurant.order'
    _description = 'Restaurant Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order_no = fields.Char(string='Order Number', required=True)
    customer_id = fields.Many2one('restaurant.customer', string='Customer')
    table_id = fields.Many2one('restaurant.table', string='Table')
    order_datetime = fields.Datetime(default=fields.Datetime.now)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('served', 'Served'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], default='draft')
    note = fields.Text()
    total_amount = fields.Float(string='Total Amount')
    order_line_ids = fields.One2many('restaurant.order.line','order_id',string='Order Lines')

    def action_calculate_total(self):
        for order in self:
            total = 0
            for line in order.order_line_ids:
                total += line.subtotal
            order.total_amount = total