# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo import SUPERUSER_ID, _, api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order" 

    y_short_close_reason = fields.Char(string='Short Close Reasons',copy=False)
    y_is_so_short_close = fields.Boolean(copy=False,string="Short Close") 

    def short_close_form_wizard_sale(self):
        if self.state == 'sale' or 'done':    
            return {
                'name': ("SaleOrder Short Close Wizard"),

                'type': 'ir.actions.act_window',

                'res_model': 'saleorder.short.close.wizard',

                'view_mode': 'form',

                'views': [(self.env.ref('odoo_e_31_b.view_saleorder_short_close_wizard_form').id, 'form')],

                'target': 'new',

                'context': dict(self._context, create=False, edit=False,default_short_close_reason =self.y_short_close_reason,default_order_id = self.id)
            }
            



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    y_is_short_close = fields.Boolean(string='Short Close',copy=False)



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

