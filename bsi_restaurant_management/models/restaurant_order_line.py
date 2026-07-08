from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RestaurantOrderLine(models.Model):
    _name = 'restaurant.order.line'
    _description = 'Restaurant Order Line'

    order_id = fields.Many2one('restaurant.order', string='Order')
    menu_id = fields.Many2one('restaurant.menu', string='Menu Item')
    quantity = fields.Integer(default=1)
    price = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal", store=True)

    @api.depends("price", "quantity")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.price * line.quantity

    @api.onchange("menu_id")
    def _onchange_menu_id(self):
        if self.menu_id:
            self.price = self.menu_id.price

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Quantity must be greater than zero.")
