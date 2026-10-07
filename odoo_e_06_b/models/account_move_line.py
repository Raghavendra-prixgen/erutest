# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError
# from odoo.tools.float_utils import float_round, float_compare
# import logging
# _logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    y_analytic_groupby_account_ids = fields.Many2many('account.analytic.account',compute="get_analytic_distribution",store=True,string="Analytical Account",copy=False)
    y_account_analytic_plan_ids = fields.Many2many('account.analytic.plan',compute="get_analytic_account_plan_ids",store=True,string="Account Analytic Plan")

    def _prepare_exchange_difference_move_vals(self, amounts_list, company=None, exchange_date=None):
        res = super()._prepare_exchange_difference_move_vals(amounts_list,company,exchange_date)
        if res.get('move_vals'):
            if res.get('move_vals').get('line_ids'):
                for line in res.get('move_vals').get('line_ids'):
                    if self.move_id.line_ids:
                        distribution = self.move_id.line_ids[0].analytic_distribution
                        line[-1].update({'analytic_distribution':distribution})
        return res

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



    @api.depends('y_analytic_groupby_account_ids')
    def get_analytic_account_plan_ids(self):
        for rec in self:
            plan_list = []
            if rec.y_analytic_groupby_account_ids:
                for account in rec.y_analytic_groupby_account_ids:
                    plan_list.append(account.plan_id.id)
                rec.y_account_analytic_plan_ids = plan_list
            else:
                rec.y_account_analytic_plan_ids = False


    def _validate_analytic_distribution(self):
        for line in self.filtered(lambda line: line.display_type not in ('line_section','line_note')):
            line._validate_distribution(**{
                        'product': line.product_id.id,
                        'account': line.account_id.id,
                        'business_domain': line.move_id.move_type in ['out_invoice', 'out_refund', 'out_receipt'] and 'invoice'
                                           or line.move_id.move_type in ['in_invoice', 'in_refund', 'in_receipt'] and 'bill'
                                           or 'general',
                        'company_id': line.company_id.id,
            })

    @api.depends('account_id', 'partner_id', 'product_id','purchase_line_id')
    def _compute_analytic_distribution(self):
        for line in self:
            distribution = False
            #Purchase
            if line.purchase_line_id:
                distribution = line.purchase_line_id.analytic_distribution 
            
            #Payment
            elif line.payment_id:
                distribution = line.payment_id.analytic_distribution
            
            #Expense
            elif line.expense_id:
                distribution = line.expense_id.analytic_distribution

            #Move Valuation
            elif line.move_id.stock_valuation_layer_ids:
                if line.move_id.stock_valuation_layer_ids.filtered(lambda svl: svl.product_id == line.product_id):
                    if line.move_id.stock_valuation_layer_ids.filtered(lambda svl: svl.product_id == line.product_id)[0].stock_move_id:
                        distribution = line.move_id.stock_valuation_layer_ids.filtered(lambda svl: svl.product_id == line.product_id)[0].stock_move_id.analytic_distribution
                    elif line.move_id.stock_valuation_layer_ids.filtered(lambda svl: svl.product_id == line.product_id)[0].account_move_line_id:
                        distribution = line.move_id.stock_valuation_layer_ids.filtered(lambda svl: svl.product_id == line.product_id)[0].account_move_line_id.analytic_distribution
            
            #Move Valuation
            # elif line.move_id.stock_valuation_layer_ids:
            #     distribution = line.move_id.stock_valuation_layer_ids.stock_move_id.analytic_distribution or line.move_id.stock_valuation_layer_ids.stock_valuation_layer_id.stock_move_id.analytic_distribution
            
            #Non-Tax
            elif not line.tax_tag_ids:
                distribution = line.move_id.line_ids[0].analytic_distribution if line.move_id.line_ids else False
            
            #Standard
            elif line.display_type == 'product' or not line.move_id.is_invoice(include_receipts=True):
                distribution = self.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.partner_id.id,
                    "partner_category_id": line.partner_id.category_id.ids,
                    "account_prefix": line.account_id.code,
                    "company_id": line.company_id.id,
                })
            
            line.analytic_distribution = distribution or line.analytic_distribution

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'
    
    def write(self, vals):
        res =  super().write(vals)
        if vals.get('account_move_id'):
            self.account_move_id.line_ids._compute_analytic_distribution()
        return res
    
    
    
class AnalyticAccountAsset(models.Model):
    _inherit = 'account.asset'

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


