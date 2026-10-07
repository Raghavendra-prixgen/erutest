# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"


    @api.onchange('categ_id')
    def _validate_categ_changer(self):
        for product in self:
            stock_quant = self.env['stock.quant'].search([('product_id.product_tmpl_id', '=',product._origin.id),('location_id.usage','=','internal'),('inventory_quantity_auto_apply','>',0)])
            quant_quantity = sum(stock_quant.mapped('inventory_quantity_auto_apply'))
            if self.categ_id and not self.env.user.has_group('odoo_e_17_b.group_prod_categ_change'):
                raise ValidationError(_("""You do not have access to change the Product Category"""))
            if quant_quantity > 0:
                    raise ValidationError(_("""Cannot Change Product category once transactions are posted. Please contact Administrator to proceed further."""))
                
    @api.onchange('tracking')
    def _onchange_tracking_new(self):
        for product in self:
            product_lot = self.env['stock.lot'].search([('product_id.product_tmpl_id', '=',product._origin.id)])
            if product_lot:
                raise ValidationError(_("""Cannot Change Tracking once transactions are posted. Please contact Administrator to proceed further."""))
            