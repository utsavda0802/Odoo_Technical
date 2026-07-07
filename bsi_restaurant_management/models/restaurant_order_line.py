from odoo import models, fields

class RestaurantOrderLine(models.Model):
    _name = 'restaurant.order.line'
    _description = 'Restaurant Order Line'

    order_id = fields.Many2one('restaurant.order', string='Order')
    menu_id = fields.Many2one('restaurant.menu', string='Menu Item')
    quantity = fields.Integer(default=1)
    price = fields.Float()
    subtotal = fields.Float()

    def action_calculate_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price