from odoo  import models,fields,api

class PurchaseOrder(models.Model):
	_inherit='purchase.order'

	gst_form_ids = fields.One2many('gst.form','purchase_order_id',string='GST Forms')