# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrderSplit(models.Model):
    _inherit = "purchase.order"
    
    y_split_id = fields.Many2one('purchase.order',string="Split Id")
    y_is_split = fields.Boolean(copy=False,string="Is Split")
    
    
    # to get the parent view of that split po
    def view_po(self):
        form_view = self.env.ref('purchase.purchase_order_form', False)
        tree_view = self.env.ref('purchase.purchase_order_kpis_tree', False)
        
        return {
            'name': 'Po',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'view_id': form_view.id,
            'domain': [('id', '=', self.y_split_id.id)],
            'views': [(tree_view.id, 'tree'),(form_view.id, 'form')],
            
        }

    
    # to get the split po wizard [po.split model view]
    def po_split_view(self):
        view = self.env.ref('odoo_e_27_b.split_po_from_view')
       
        return {
                'name': _('Split PO'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'po.split',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
              
                }
    
    
    
class SplitPoWizard(models.Model):
    _name = 'po.split'
    
    y_purchase_id = fields.Many2one('purchase.order',"Purchase Order")
    y_partner_id = fields.Many2one('res.partner',"Partner")
    y_split_ids = fields.One2many('po.split.line','y_po',string="split lines")
    
    
    
    
    # to get purchase order o2m value to the o2m of po.split wizard  or form
    @api.model
    def default_get(self, fields):
        res = super(SplitPoWizard, self).default_get(fields)
        list_new = self.env['purchase.order'].browse(self._context.get('active_ids', False))
        self.y_purchase_id = list_new
        
        po_list = []
        for rec in list_new.order_line:
            
            po_list.append((0, 0, {'y_product_id': rec.product_id.id, 'y_po_quantity': rec.product_qty, 'y_purchase_line_id': rec.id}))
            
        res['y_split_ids'] = po_list
        return res
    
    
    
    
    
    def button_split_po(self):
        # add_val = []
        list_new_sp = self.env['purchase.order'].browse(self._context.get('active_ids', False))
        
        for rec in self:
            
            for s_po in rec.y_split_ids:
            
                s_po.y_purchase_line_id.product_qty = s_po.y_purchase_line_id.product_qty - s_po.y_po_quantity
                
                if s_po.y_purchase_line_id.product_qty <= 0:
                    po_value = self.env['purchase.order.line'].search([('id', '=', s_po.y_purchase_line_id.id),('product_qty', '<=', 0.0)])
                    
                    po_value.unlink()
                 
            val = {
                    'partner_id' : rec.y_partner_id.id,
                    'y_split_id'   : list_new_sp.id,
                    'y_is_split'   : True,
                    'order_line' : [(0,0,{'product_id':so.y_product_id.id,'product_qty':so.y_po_quantity}) for so in rec.y_split_ids],
                    
                }
            
            records = self.env['purchase.order'].create(val)  
            
            
           
            

    
class SplitPoLine(models.Model):
    _name = 'po.split.line'
    
    y_po = fields.Many2one('po.split',string = "po split name")
    y_product_id = fields.Many2one('product.product',string = "Product")
    y_po_quantity = fields.Float("Quantity")
    y_purchase_line_id = fields.Many2one('purchase.order.line',"Purchase Order")
    
    
    
    @api.constrains('y_po_quantity')
    def _check_quantity(self):
       
        for qty in self:
            if qty.y_po_quantity > qty.y_purchase_line_id.product_qty:
                raise ValidationError(_("Split Quantity Value Should [y_po_quantity] Exceed Than Quantity [product_qty] of Purchase Order Line "))
                
    
    
    


    