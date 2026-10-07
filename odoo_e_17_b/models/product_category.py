# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError


class ProductCategory2(models.Model):
    _name = "product.category"
    _inherit = ['product.category','portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    parent_id = fields.Many2one(tracking=True)
    name = fields.Char(tracking=True)
    removal_strategy_id = fields.Many2one(tracking=True)
    property_account_creditor_price_difference_categ = fields.Many2one(tracking=True)
    property_account_income_categ_id = fields.Many2one(tracking=True)
    property_account_expense_categ_id = fields.Many2one(tracking=True)
    property_valuation = fields.Selection(tracking=True)
    property_cost_method = fields.Selection(tracking=True)
    property_stock_journal = fields.Many2one(tracking=True)
    property_stock_account_input_categ_id = fields.Many2one(tracking=True)
    property_stock_account_output_categ_id = fields.Many2one(tracking=True)
    property_stock_valuation_account_id = fields.Many2one(tracking=True)
    y_release = fields.Boolean(tracking=True)


    @api.onchange('property_cost_method')
    def _onchange_property_cost_new(self):
        for rec in self:
            line_ids = self.env['account.move.line'].search([('product_id.categ_id','=',rec._origin.id)])
            if line_ids:
                raise ValidationError(_("""Cannot Change Costing Method once transactions are posted. Please contact Administrator to proceed further."""))
            