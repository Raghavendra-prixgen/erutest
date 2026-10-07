# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo import SUPERUSER_ID, _, api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order" 

    def short_close_form_wizard(self):
        po_lines=self.order_line.filtered(lambda line: line.y_is_short_close == False and line.product_qty != line.qty_received)            
        if self.state == 'purchase' or 'done' and po_lines:    
            return {
                'name': ("Purchase Short Close Wizard"),

                'type': 'ir.actions.act_window',

                'res_model': 'purchase.short.close.wizard',

                'view_mode': 'form',

                'views': [(self.env.ref('odoo_e_27_b.view_purchase_short_close_wizard_form').id, 'form')],

                'target': 'new',

                'context': dict(self._context,default_y_short_close_reason =self.y_short_close_reason,default_y_purchase_id=self.id,default_sc_po_lines_ids = po_lines.ids)
            }


    y_short_close_reason = fields.Char(string='Short Close Reasons',copy=False)
    y_is_po_short_close = fields.Boolean(copy=False,string="Short Close") 

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    y_is_short_close = fields.Boolean(string='Short Close',copy=False)

    y_recieved_qty = fields.Boolean(compute="check_fields_equals")


    # @api.depends('product_qty','qty_received')
    # def check_fields_equals(self):
    #     for rec in self:
    #         if rec.product_qty == rec.qty_received:
    #             rec.y_recieved_qty=True
    #         else:
              
    #             rec.y_recieved_qty = False
    



class StockMove(models.Model):
    _inherit = "stock.move"

    y_is_freeze = fields.Boolean(copy=False)

    #If move freeze is True the related moves i.e. user should not be able to update done qty for those moves

    # @api.onchange('quantity')
    # def _onchange_done_qty_freeze(self):
    #     for rec in self:
    #         if rec.y_is_freeze == True:
    #             raise ValidationError('You cannot change Done Qty It is in Short Close')

    #END

