# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import api, models, fields,tools, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import UserError, ValidationError


class MrpWorkCenter(models.Model):
    _inherit = "mrp.workcenter"

    y_workcenter_landed_cost_lines_ids = fields.One2many('workcenter.landed.cost.lines','y_workcenter_id')



class WorkcenterLandedCost(models.Model):
    _name = "workcenter.landed.cost.lines"

    y_product_id = fields.Many2one('product.product',string="Product")
    y_method_type = fields.Selection([('hours', 'Hours'),
                                    ('qty', 'Qty'),
                                    ('percentage', 'Percentage'),
                                    ('fixed_amount', 'Fixed Amount'),
                                    ], string='Type')
    y_cost_per_hr = fields.Float(string="Cost Per")
    # unit_cost = fields.Float(string="Unit Cost")
    # value = fields.Float(string="Value")
    # fixed = fields.Float(string="Amount")
    y_workcenter_id = fields.Many2one('mrp.workcenter')


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
    
        res = super().button_mark_done()
        for rec in self:
            for workorder in rec.workorder_ids:
                for workorder_landed_cost_lines in workorder.workcenter_id.y_workcenter_landed_cost_lines_ids:
                  
                    cost = 0
                    if workorder_landed_cost_lines.y_method_type == 'hours':
                        cost = (workorder.duration * workorder_landed_cost_lines.y_cost_per_hr)

                    elif workorder_landed_cost_lines.y_method_type == 'qty':
                        cost = (workorder.y_total_output_quantity * workorder_landed_cost_lines.y_cost_per_hr)

                    elif workorder_landed_cost_lines.y_method_type == 'percentage':
                        svl_obj = self.env['stock.valuation.layer'].search([('reference','=',rec.name),('y_product_id','=',rec.y_product_id.id)],limit=1)
                        cost = (svl_obj.value * workorder_landed_cost_lines.y_cost_per_hr)/100

                    elif workorder_landed_cost_lines.y_method_type == 'fixed_amount':
                        cost = workorder_landed_cost_lines.y_cost_per_hr


                    land_cost_vals=self.env['stock.landed.cost.lines'].create({
                                'product_id':workorder_landed_cost_lines.y_product_id.id,
                                'name':workorder_landed_cost_lines.y_product_id.name,
                                'account_id':workorder_landed_cost_lines.y_product_id.property_account_expense_id.id,
                                'split_method':workorder_landed_cost_lines.y_product_id.split_method_landed_cost,
                                'price_unit':cost
                                })
                    val = self.env['stock.landed.cost'].create({
                        'mrp_production_ids':[(4, rec.id)],
                        'target_model':'manufacturing',
                        'cost_lines':[(6, 0, land_cost_vals.ids)]
                        })
                    val.compute_landed_cost()
                    val.button_validate()

        return res


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"


    y_product_ids = fields.Many2many('product.product',string="Service Products",store=True)

    @api.model
    def create(self,vals):
        if vals.get('stock_landed_cost_id') :
            landedcost_obj = self.env['stock.landed.cost'].browse(vals.get('stock_landed_cost_id'))
            vals['y_product_ids'] = landedcost_obj.cost_lines.mapped('product_id')
        return super().create(vals)






