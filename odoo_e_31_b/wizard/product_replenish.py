# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context


class Saleremarks(models.TransientModel):
    _name = 'sale.approval.remarks'
    _description = 'sale.approval.remarks'

    product_id = fields.Char( string='Remaks', required=True)
    
    # @api.model
    # def default_get(self, fields):
    #     res = super(ProductReplenish, self).default_get(fields)
    #     product_tmpl_id = self.env['product.template']
    #     if 'product_id' in fields:
    #         if self.env.context.get('default_product_id'):
    #             product_id = self.env['product.product'].browse(self.env.context['default_product_id'])
    #             product_tmpl_id = product_id.product_tmpl_id
    #             res['product_tmpl_id'] = product_id.product_tmpl_id.id
    #             res['product_id'] = product_id.id
    #         elif self.env.context.get('default_product_tmpl_id'):
    #             product_tmpl_id = self.env['product.template'].browse(self.env.context['default_product_tmpl_id'])
    #             res['product_tmpl_id'] = product_tmpl_id.id
    #             res['product_id'] = product_tmpl_id.product_variant_id.id
    #             if len(product_tmpl_id.product_variant_ids) > 1:
    #                 res['product_has_variants'] = True
    #     company = product_tmpl_id.company_id or self.env.company
    #     if 'product_uom_id' in fields:
    #         res['product_uom_id'] = product_tmpl_id.uom_id.id
    #     if 'company_id' in fields:
    #         res['company_id'] = company.id
    #     if 'warehouse_id' in fields and 'warehouse_id' not in res:
    #         warehouse = self.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
    #         res['warehouse_id'] = warehouse.id
    #     if 'date_planned' in fields:
    #         res['date_planned'] = datetime.datetime.now()
    #     return res

    # def launch_replenishment(self):
    #     uom_reference = self.product_id.uom_id
    #     self.quantity = self.product_uom_id._compute_quantity(self.quantity, uom_reference)
    #     try:
    #         self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
    #             self.env['procurement.group'].Procurement(
    #                 self.product_id,
    #                 self.quantity,
    #                 uom_reference,
    #                 self.warehouse_id.lot_stock_id,  # Location
    #                 _("Manual Replenishment"),  # Name
    #                 _("Manual Replenishment"),  # Origin
    #                 self.warehouse_id.company_id,
    #                 self._prepare_run_values()  # Values
    #             )
    #         ])
    #     except UserError as error:
    #         raise UserError(error)
