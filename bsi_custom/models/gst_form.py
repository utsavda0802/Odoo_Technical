from odoo import models,fields,api

class GstForm(models.Model):
	_name = 'gst.form'
	_description = 'GST Forms'

	name = fields.Char(string='Reference Number',readonly=True,copy=False,default='New')
	purchase_order_id = fields.Many2one('purchase.order',string='Purchase Order',required = True)
	applicable_amount = fields.Float(string='Appliccable Amount',required=True)
	gst_percentage = fields.Float(string='GST Percentage',required=True)
	gst_amount = fields.Float(string='GST Amount',compute='_compute_gst_amount',store=True)
	old_gst_amount = fields.Float(string='Old GST Amount')
	new_gst_amount = fields.Float(string='New GST Amount')
	gst_difference = fields.Float(string='Difference')

	@api.depends('applicable_amount','gst_percentage')
	def _compute_gst_amount(self):
		for rec in self:
			rec.gst_amount = rec.applicable_amount*rec.gst_percentage/100

	@api.model_create_multi
	def create(self,vals_list):
		for vals in vals_list:
			if vals.get('name','New') == 'New':
				today = fields.Date.context_today(self)
				prefix = f"GST/{today:%m}/{today:%Y}/"

				last_record = self.search([('name','like',prefix)], order = 'id desc',limit=1)
				if last_record:
					last_number = int(last_record.name.split('/')[-1])
				else:
					last_number=0
				vals['name'] = prefix + str(last_number + 1).zfill(6)

			amount = vals.get('applicable_amount',0)
			percentage = vals.get('gst_percentage',0)
			gst_amount = amount*percentage/100

			vals['gst_amount'] = gst_amount
			vals['new_gst_amount'] = gst_amount
			vals['old_gst_amount'] = 0

		record = super(GstForm,self).create(vals_list)
		return record


	def write(self,vals):
		for rec in self:
			old_amount = rec.gst_amount

			amount = vals.get('applicable_amount',rec.applicable_amount)
			percentage = vals.get('gst_percentage',rec.gst_percentage)
			new_amount = amount * percentage / 100

			vals['gst_amount'] = new_amount
			vals['old_gst_amount'] = old_amount
			vals['new_gst_amount'] = new_amount
			vals['gst_difference'] = new_amount - old_amount

			super(GstForm,rec).write(vals)
		return True