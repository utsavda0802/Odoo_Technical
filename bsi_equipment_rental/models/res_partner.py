from odoo import models, fields, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _name = 'res.partner'          
    _inherit = 'res.partner'
    _description = 'Contact'       
    
    is_rental_customer = fields.Boolean(string='Is Rental Customer', default=False)

    rental_ids = fields.One2many('rental.order', 'partner_id', string='Rentals')
    rental_count = fields.Integer(string='Rental Count', compute='_compute_rental_count')

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

    def unlink(self):
        for partner in self:
            if partner.rental_ids:
                raise UserError(
                    f"Cannot delete '{partner.name}' — they have existing rental records."
                )
        return super().unlink()