# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError

class ChoosePurchaseCharges(models.TransientModel):
    _name = 'choose.purchase.charges'
    _description = 'purchase Charges Selection Wizard'
    
    y_purchase_id = fields.Many2one('purchase.order', ondelete="cascade")
    y_product_id = fields.Many2one('product.product', string='Charges',domain="[('detailed_type', '=', 'service')]")
    y_unit_price = fields.Float("Cost")

    @api.onchange('y_product_id')
    def check_is_landed_cost(self):
        if self.y_product_id and   not self.y_product_id.split_method_landed_cost:
            raise UserError(_('Split method is not configured for the %s in the Masters')% (self.y_product_id.name))

        if self.y_product_id and  not self.y_product_id.landed_cost_ok:
            raise UserError(_('Is a Landed Cost is not configured for the %s in Masters')% (self.y_product_id.name))
            
    def action_put_in_charges(self):
        y_purchase_id = self.env['purchase.order'].browse(self._context.get('po_id'))
        self.y_purchase_id = y_purchase_id.id
        y_product_id = self.y_product_id
        y_unit_price = self.y_unit_price
        self.y_purchase_id._create_purchase_charge_line(y_product_id,y_unit_price)
        