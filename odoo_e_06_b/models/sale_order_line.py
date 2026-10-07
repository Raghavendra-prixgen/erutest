# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError
# from odoo.tools.float_utils import float_round, float_compare
# import logging
# _logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    y_dist_mo_id = fields.Many2one('mrp.production',copy=False)
    y_analytic_groupby_account_ids = fields.Many2many('account.analytic.account',compute="get_analytic_distribution",store=True,string="Analytical Account")


    @api.depends('analytic_distribution')
    def get_analytic_distribution(self):
        for rec in self:
            if rec.analytic_distribution:
                analytic_ids = []
                for analytic_keys in rec.analytic_distribution.keys():
                    for analytic_key in analytic_keys.split(','):
                        int_analytic_key = int(analytic_key)
                        analytic_account_obj = rec.env['account.analytic.account'].search([('id','=',int_analytic_key)])
                        if analytic_account_obj.active:
                            analytic_ids.append(analytic_account_obj.id)
                rec.y_analytic_groupby_account_ids = analytic_ids
            else:
                rec.y_analytic_groupby_account_ids = False




    @api.depends('order_id.partner_id', 'product_id','order_id.warehouse_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type :
                distribution = line.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.order_id.partner_id.id,
                    "partner_category_id": line.order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                    "y_warehouse_id": line.order_id.warehouse_id.id,
                    # "user_ids": self.env.user.id,
                })
                line.analytic_distribution = distribution or line.analytic_distribution
