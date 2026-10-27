from odoo import fields,models

class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Asset Category'

    name = fields.Char(required=True)
    useful_life = fields.Integer(string='Useful Life (Years)',default = 3)
    depreciation_type = fields.Selection([('straight_line','Straight Line'),('none','No Depreciation')] , default='straight_line', required=True)
    