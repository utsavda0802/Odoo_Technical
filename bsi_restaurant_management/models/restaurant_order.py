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

    def action_orm_methods(self):
        OrderLine = self.env['restaurant.order.line']
        Menu = self.env['restaurant.menu']

        # 1. search() - find records matching a domain
        lines = OrderLine.search([('price', '>', 150), ('menu_id.name', '=', 'pizza')])
        print(f"SEARCH: {lines}".center(150, '-'))

        # 2. search_count() - just get the count, cheaper than len(search())
        count = OrderLine.search_count([('price', '>', 150)])
        print(f"SEARCH_COUNT: {count}".center(150, '-'))

        # 3. browse() - get a recordset by known id(s), no DB query for existence
        line = OrderLine.browse(1)
        print(f"BROWSE: {line}".center(150, '-'))

        # 4. create() - insert a new record
        new_menu = Menu.create({
            'name': 'Ice Cream',
            'description': 'test item',
            'price': 80,
        })
        print(f"CREATE: {new_menu}".center(150, '-'))

        new_line = OrderLine.create({
            'menu_id': new_menu.id,
            'order_id': self.id,
            'quantity': 2,
        })
        print(f"CREATE LINE: {new_line}".center(150, '-'))

        # 5. copy() - duplicate a record (optionally override some fields)
        copied_line = new_line.copy({'quantity': 5})
        print(f"COPY: {copied_line}".center(150, '-'))

        # 6. write() - update field(s) on existing record(s)
        new_line.write({'quantity': 3})
        print(f"WRITE: {new_line.quantity}".center(150, '-'))

        # 7. read() - fetch specific fields as a list of dicts (lighter than looping recordset)
        data = new_line.read(['quantity', 'menu_id', 'price'])
        print(f"READ: {data}".center(150, '-'))

        # 8. flush() - force pending ORM changes to the DB immediately
        #    (useful before raw SQL, or when you need DB-level constraints/triggers
        #    to see uncommitted changes within the same transaction)
        self.env.flush_all()  # or new_line.flush_recordset() for a specific model

        # 9. unlink() - delete record(s). Do this LAST since it removes what we just made
        copied_line.unlink()
        print("UNLINK: copied_line deleted".center(150, '-'))

