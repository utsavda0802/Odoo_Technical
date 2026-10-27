from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:

            print("\n" + "==" * 25)
            print("Sale Order is confirmed")
            print("Sale Order:- " + order.name)
            print(order.partner_id.name)
            print("==" * 25 + "\n")

            buyer_company = self.env['res.company'].search([('partner_id', '=', order.partner_id.id)], limit=1)

            if buyer_company:
                seller_company = order.company_id

                if buyer_company == seller_company:
                    print("Skipping: buyer and seller are the same company entity")
                    continue

                print("Target buyer company Found.")
                print(buyer_company.name)

                buyer_context = self.env.context.copy()
                buyer_context.update({
                    'allowed_company_ids': [buyer_company.id],
                    'company_id': buyer_company.id
                })
                buyer_env = self.env(context=buyer_context)

                po_env = buyer_env['purchase.order']
                po_line_env = buyer_env['purchase.order.line']

                vendor_profile = seller_company.partner_id

                if vendor_profile:
                    print("Matching vendor profile found.")
                    print(vendor_profile.name)

                    po_vals = {
                        'partner_id': vendor_profile.id,
                        'company_id': buyer_company.id,
                        'origin': order.name,
                        'date_order': fields.Datetime.now(),
                    }

                    new_po = po_env.create(po_vals)

                    print("Purchase Order header created")
                    print(new_po.name)

                    for line in order.order_line:
                        if line.display_type:
                            continue

                        product_in_buyer = buyer_env['product.product'].browse(line.product_id.id)

                        po_line_env.create({
                            'order_id': new_po.id,
                            'product_id': product_in_buyer.id,
                            'name': line.name or product_in_buyer.display_name,
                            'product_qty': line.product_uom_qty,
                            'product_uom_id': line.product_uom_id.id,
                            'date_planned': fields.Datetime.now(),
                        })

                        print("Purchase order line created for product.")
                        print(product_in_buyer.display_name)

                    print("Confirming Purchase Order...")
                    new_po.button_confirm()

                    print("Validating Delivery Receipt...")
                    for picking in new_po.picking_ids:
                        if picking.state not in ['done', 'cancel']:
                            # Set quantities automatically
                            picking.action_assign()
                            for move in picking.move_ids:
                                move.quantity = move.product_uom_qty
                            # Validate the transfer
                            picking.button_validate()
                            print(f"Receipt {picking.name} Validated.")

                    print("Creating Vendor Bill...")

                    action = new_po.action_create_invoice()
                    
                    # Find the draft bill that was just created
                    invoice_ids = action.get('res_id') or action.get('domain', [])
                    bills = buyer_env['account.move'].browse(invoice_ids)
                    
                    for bill in bills:

                        bill.invoice_date = fields.Date.context_today(self)
                        
                        bill.action_post()
                        print(f"Vendor Bill {bill.name} Created and Posted.")

                else:
                    print("Error: vendor profile not found for seller company.")

            else:
                print("Skipping: customer does not belong to another company.")

        return res