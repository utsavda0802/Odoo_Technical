from odoo import models, fields

class RentalEquipment(models.Model):
    _name = 'rental.equipment'
    _description = 'Rental Equipment'

    name = fields.Char(string='Equipment Name', required=True)
    code = fields.Char(string='Equipment Code')
    category = fields.Selection([
        ('camera', 'Camera'),
        ('drone', 'Drone'),
        ('projector', 'Projector'),
        ('tool', 'Tool'),
    ], string='Category', default='camera')

    status = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
    ], string='Status', default='available')

    price_per_day = fields.Float(string='Price per Day')
    security_deposit = fields.Float(string='Security Deposit')

    _code_unique = models.Constraint('UNIQUE(code)','Equipment code must be unique')
    _deposit_positive = models.Constraint('CHECK(security_deposit >= 0)', 'SECURITY DEPOSIT CANNOT BE NEGATIVE')