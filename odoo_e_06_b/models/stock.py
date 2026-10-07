# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError
# from odoo.tools.float_utils import float_round, float_compare
# import logging
# _logger = logging.getLogger(__name__)



class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = ['stock.move','analytic.mixin']

    y_is_inv_adjust_move = fields.Boolean('Is Inv Adjust Move')

    y_analytic_groupby_account_ids = fields.Many2many('account.analytic.account',compute="get_analytic_distribution",store=True,string="Analytical Account")

    y_account_analytic_plan_ids = fields.Many2many('account.analytic.plan',compute="get_analytic_account_plan_ids",store=True,string="Account Analytic Plan")

    #for server action
    def update_json_analytic(self):
        for rec in self:
            if rec.analytic_distribution:
                analytic_ids = []
                for analytic_key in rec.analytic_distribution.keys():
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



    def _action_done(self, cancel_backorder=False):
        for move in self:
            move._validate_analytic_distribution()
        return super(StockMove, self)._action_done(cancel_backorder)

    @api.depends('purchase_line_id', 'purchase_line_id.analytic_distribution','sale_line_id', 'sale_line_id.analytic_distribution','production_id', 'production_id.analytic_distribution','raw_material_production_id', 'raw_material_production_id.analytic_distribution')
    def _compute_analytic_distribution(self):
        for line in self:
            distribution = \
                line.purchase_line_id.analytic_distribution if line.purchase_line_id\
                else line.sale_line_id.analytic_distribution if line.sale_line_id\
                else line.production_id.analytic_distribution if line.production_id\
                else line.raw_material_production_id.analytic_distribution if line.raw_material_production_id\
                else line.group_id.mrp_production_ids[0].analytic_distribution if len(line.group_id.mrp_production_ids)\
                else line.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "company_id": line.company_id.id,
                    "y_warehouse_id": line.picking_id.picking_type_id.warehouse_id.id,
                    # "user_ids": self.env.user.id,
                })
            line.analytic_distribution = distribution or line.analytic_distribution
    
    def _validate_analytic_distribution(self):
        for line in self:
            if line.purchase_line_id or line.sale_line_id or line.y_is_inv_adjust_move or line.production_id or line.raw_material_production_id:
                #enforce analytic validation
                line.with_context(validate_analytic = True)._validate_distribution(**{
                    'product': line.product_id.id,
                    'business_domain': 'stock_move_and_line',
                    'company_id': line.company_id.id,
                })


class StockInventoryAdjustmentName(models.TransientModel):
    _name = 'stock.inventory.adjustment.name'
    _inherit = ['stock.inventory.adjustment.name','analytic.mixin']

    def action_apply(self):
        quants = self.quant_ids.filtered('inventory_quantity_set')
        return quants.with_context(inventory_name=self.inventory_adjustment_name,analytic_distribution=self.analytic_distribution).action_apply_inventory()

  

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, package_id=False, package_dest_id=False):
        res = super()._get_inventory_move_values(qty, location_id, location_dest_id, package_id, package_dest_id)

        res['analytic_distribution'] = self.env.context.get('analytic_distribution',False)
        res['y_is_inv_adjust_move'] = True

        return res


    
    def action_stock_inventory_adjustement(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_stock_inventory_adjustement_name"
        )
        return action

class StockValutionLayer(models.Model):
    _name = "stock.valuation.layer"
    _inherit = ['stock.valuation.layer','analytic.mixin']

    y_analytic_groupby_account_ids = fields.Many2many('account.analytic.account',compute="get_analytic_distribution",store=True,string="Analytical Account")
    y_account_analytic_plan_ids = fields.Many2many('account.analytic.plan',compute="get_analytic_account_plan_ids",store=True,string="Account Analytic Plan")


    @api.depends('account_move_id', 'product_id', 'stock_move_id')
    def _compute_analytic_distribution(self):
        for line in self:
            distribution = False
            #StockMove
            if line.stock_move_id:
                distribution = line.stock_move_id.analytic_distribution 
            
            #AccoutMoveLine
            elif line.account_move_id:
                distribution = line.account_move_id.line_ids[0].analytic_distribution if line.account_move_id.line_ids else False
            
            line.analytic_distribution = distribution or line.analytic_distribution



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


    #for server action
    def update_json_analytic(self):
        for rec in self:
            if rec.analytic_distribution:
                analytic_ids = []
                for analytic_key in rec.analytic_distribution.keys():
                    int_analytic_key = int(analytic_key)
                    analytic_account_obj = rec.env['account.analytic.account'].search([('id','=',int_analytic_key)])
                    if analytic_account_obj.active:
                        analytic_ids.append(analytic_account_obj.id)
                rec.y_analytic_groupby_account_ids = analytic_ids
            else:
                rec.y_analytic_groupby_account_ids = False