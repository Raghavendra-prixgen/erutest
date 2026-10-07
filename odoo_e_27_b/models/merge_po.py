
from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import AccessError, UserError, ValidationError
import time



class PurchaseorderNew(models.Model):
    _inherit = "purchase.order"

    y_cancel_po_bool = fields.Boolean(string="Cancel Po Bool")
    y_parent_rfq_ref = fields.Many2one('purchase.order',string="Parent Rfq Ref")
    y_warehouse_id = fields.Many2one("stock.warehouse", related="picking_type_id.warehouse_id")


    def merge_po(self):
        rfq_state = self.mapped('state') 
        if 'draft' in rfq_state:
            customer_val = self.mapped('partner_id')
            y_doc_type_id_val = self.mapped('y_doc_type_id')
            company_id_val  = self.mapped('company_id')
            mrp_count_value = sum(self.mapped('mrp_production_count'))
            if 'cancel' in rfq_state:
                raise UserError(_("Select the Cancel State Purchase Order"))   
            if len(customer_val)>1:
                raise UserError(_("Select the RFQ's with same vendor"))
            if len(y_doc_type_id_val)>1:
                raise UserError(_("Select the RFQ's with same Document Type"))
            if len(company_id_val)>1:
                raise UserError(_("Select the RFQ's with same Company"))
         
            total_source_doc = self.mapped('origin')
            source_document = ""
            if total_source_doc:
                if all(total_source_doc) == True:
                    total_source_doc = set(total_source_doc)
                    source_document = ','.join(total_source_doc)

            total_rfq = self.mapped('name')
            if total_rfq:
                y_quotation_number = ','.join(total_rfq)



           
            # total_saleorder_ref = self.mapped('y_so_origin')
            # saleorder_ref = ""
            # if total_saleorder_ref:
            #     if all(total_saleorder_ref) == True:
            #         total_saleorder_ref = set(total_saleorder_ref)
            #         saleorder_ref = ','.join(total_saleorder_ref)
            

            
            purchase_order = self.env['purchase.order'].create({
                            'partner_id': self.mapped('partner_id')[0].id,
                            # 'l10n_in_gst_treatment':self.mapped('l10n_in_gst_treatment')[0] if self.mapped('l10n_in_gst_treatment') else "",
                            'y_doc_type_id':self.mapped('y_doc_type_id')[0].id if self.mapped('y_doc_type_id') else "",
                            'currency_id':self.mapped('currency_id')[0].id if self.mapped('currency_id') else "",
                            'date_order':self.mapped('date_order')[0] if self.mapped('date_order') else "",
                            'picking_type_id':self.mapped('picking_type_id')[0].id if self.mapped('picking_type_id') else "",
                            'y_partner_category_id':self.mapped('y_partner_category_id')[0].id if self.mapped('y_partner_category_id') else "",
                            'origin':source_document if source_document else "",
                            # 'y_so_origin':saleorder_ref if saleorder_ref else "",
                            'company_id':self.mapped('company_id')[0].id,
                            'y_warehouse_id':self.mapped('y_warehouse_id')[0].id if self.mapped('y_warehouse_id') else "",
                            'payment_term_id':self.mapped('payment_term_id')[0].id if self.mapped('payment_term_id') else "",
                            'y_quotation_number':y_quotation_number if y_quotation_number else "",
                            'mrp_production_count':mrp_count_value,
                            
                            })
            product=[]
            for po_line in self.order_line:
                if po_line.product_id not in product:
                    purchase_order.order_line=[(0,0,{
                                                    'product_id': po_line.product_id.id ,
                                                    'name': po_line.product_id.name,
                                                    'product_qty': po_line.product_qty,
                                                    'product_uom':po_line.product_uom.id,
                                                    'price_unit':po_line.price_unit,
                                                    'taxes_id':po_line.taxes_id.ids,
                                                    'price_subtotal':po_line.price_subtotal,
                                                    'move_dest_ids':po_line.move_dest_ids.ids,
                                                    'move_ids':po_line.move_ids.ids
                                                    },
                                            )]

                    product.append(po_line.product_id)
                else:
                    product_qty_val = sum(self.order_line.filtered(lambda x:x.product_id==po_line.product_id).mapped('product_qty'))

                    purchase_order.order_line = [(1, purchase_order.order_line.filtered(lambda x:x.product_id==po_line.product_id).id, {'product_qty':product_qty_val})]
            for cancel_order in self:
                cancel_order.y_cancel_po_bool = True
                cancel_order.state = 'cancel'
                cancel_order.y_parent_rfq_ref = purchase_order.id


            stock_move_val = self.env['stock.move'].search([('created_purchase_line_ids.order_id','in',self.mapped('id'))])
            for stock_move in stock_move_val:

                stock_move.created_purchase_line_ids = purchase_order.order_line.filtered(lambda x:x.product_id==stock_move.product_id).id
          
        else:
            raise UserError(_("Only RFQ's can be merge"))









