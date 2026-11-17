from odoo import api,fields,models
from odoo.exceptions import UserError,ValidationError

class Asset(models.Model):
    _name = 'asset.asset'
    _description = 'Asset'
    _inherit = ['mail.thread','mail.activity.mixin']

    tag = fields.Char(string='Asset Tag',readonly=True,copy=False)
    name = fields.Char(string='Asset Name',required=True,tracking=True)
    category_id = fields.Many2one('asset.category',string='Category',tracking=True)
    brand = fields.Char()
    model_number = fields.Char()
    serial_number = fields.Char()

    purchase_date = fields.Date()
    purchase_price = fields.Float()
    vendor = fields.Char("Vendor Name")
    warranty_end_date = fields.Date()

    employee_id = fields.Many2one('hr.employee',string='Assigned To',tracking = True)
    assigned_date = fields.Date(readonly=True,copy=False)
    unassigned_date = fields.Date(readonly=True,copy=False)
    location = fields.Selection([('office','Office'),('warehouse','Warehouse'),('remote','Remote'),('in_repair','In Repair')],default='office',tracking=True)
    condition = fields.Selection([('new','New'),('good','Good'),('fair','Fair'),('poor','Poor'),('disposed','Disposed')],default='new',tracking=True,required=True)

    current_value = fields.Float(string='Current Value',compute='_compute_current_value')
    warranty_expired = fields.Boolean(string='Warranty Expired',compute='_compute_warranty')
    warranty_days_remaining = fields.Integer(string='Warranty Days Remaining',compute='_compute_warranty')
    reminder_sent = fields.Boolean(copy=False)

    @api.depends('purchase_price','purchase_date','category_id.useful_life','category_id','category_id.depreciation_type')
    def _compute_current_value(self):
        today = fields.Date.today()
        for rec in self :
            value = rec.purchase_price
            cat = rec.category_id
            if (cat and cat.depreciation_type =='straight_line'and cat.useful_life > 0 and rec.purchase_date):
                years = (today - rec.purchase_date).days / 365.25
                if years >= cat.useful_life:
                    value = 0
                else:
                    value = rec.purchase_price - (rec.purchase_price/cat.useful_life) * years
            rec.current_value = value

    @api.depends('warranty_end_date')
    def _compute_warranty(self):
        today = fields.Date.today()
        for rec in self:
            if rec.warranty_end_date:
                days = (rec.warranty_end_date - today).days
                rec.warranty_days_remaining = days
                rec.warranty_expired = days < 0
            else:
                rec.warranty_expired = False
                rec.warranty_days_remaining = 0

    
    @api.onchange('purchase_date', 'warranty_end_date')
    def _onchange_warranty(self):
        if (self.warranty_end_date and self.warranty_end_date < fields.Date.today()):
            return {
                'warning': {
                    'title': 'Warranty Expired',
                    'message': 'The warranty for this asset has already expired.',
                }
            }

    @api.constrains('serial_number')
    def _check_serial_number(self):
        for rec in self:
            if rec.serial_number:
                other = self.search([('serial_number', '=', rec.serial_number), ('id', '!=', rec.id)], limit=1)
                if other:
                    raise ValidationError("The serial number must be unique. An asset with this serial number already exists.")

    @api.constrains('employee_id', 'condition')
    def _check_disposed_assignment(self):
        for rec in self:
            if rec.condition == 'disposed' and rec.employee_id:
                raise ValidationError("A disposed asset cannot be assigned to an employee.")

    @api.model_create_multi
    def create(self, vals_list):
        today = fields.Date.today()
        for vals in vals_list:
            if not vals.get('tag'):
                vals['tag'] = self.env['ir.sequence'].next_by_code('asset.asset') 
            if vals.get('employee_id'):
                vals['assigned_date'] = today
        return super().create(vals_list)

    def write(self, vals):
        today = fields.Date.today()
        if 'condition' in vals:
            for rec in self:
                if rec.condition == 'disposed' and vals['condition'] != 'disposed':
                    raise UserError("A disposed asset cannot go back to another condition.")
        if 'warranty_end_date' in vals:
            vals['reminder_sent'] = False
        if 'employee_id' in vals:
            for rec in self:
                if vals['employee_id'] != rec.employee_id.id:
                    if vals['employee_id']:
                        rec.write({'assigned_date': today, 'unassigned_date': False})
                    else:
                        rec.write({'unassigned_date': today})
        return super().write(vals)

    def unlink(self): 
        for rec in self:
            if rec.condition == 'disposed':
                raise UserError("Disposed assets cannot be deleted.")
            if rec.employee_id:
                raise UserError("Unassigned the asset from the employee before deleting.")
        return super().unlink()

    def _move_condition(self,from_condition,to_condition):
        for rec in self:
            if rec.condition != from_condition:
                raise UserError(f"Asset {rec.name} is not in the '{from_condition}' condition.")
            rec.condition = to_condition

    def action_set_good(self):
        self._move_condition('new','good')

    def action_set_fair(self):
        self._move_condition('good','fair')

    def action_set_poor(self):
        self._move_condition('fair','poor')

    def action_dispose(self):
        if not self.env.user.has_group('bsi_asset_tracking.group_asset_manager'):
            raise UserError("Only asset managers can dispose of assets.")
        for rec in self:
            if rec.condition == 'disposed':
                raise UserError("This asset is already disposed.")
            rec.write({'employee_id': False, 'condition': 'disposed'})

    def _cron_warranty_reminder(self):
        today = fields.Date.today()
        last_day = fields.Date.add(today, days=7)
        assets = self.search([
            ('warranty_end_date', '>=', today),
            ('warranty_end_date', '<=', last_day),
            ('employee_id', '!=', False),
            ('reminder_sent', '=', False),
        ])
        for asset in assets:
            manager_user = asset.employee_id.parent_id.user_id
            if not manager_user:
                continue
            asset.activity_schedule(
                'mail.mail_activity_data_todo',
                summary='Warranty Expiration Reminder',
                note=f'The warranty for asset "{asset.name}" (Tag: {asset.tag}) is expiring on {asset.warranty_end_date}.',
                user_id=manager_user.id,
                date_deadline = asset.warranty_end_date,
            )
            asset.reminder_sent = True
            