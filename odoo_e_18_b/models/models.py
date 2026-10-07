# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import api, models, fields,tools, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import UserError, ValidationError


class ProducttemplateNew(models.Model):
    _inherit = "product.template"

    y_automated_landed_cost = fields.Boolean(string="Automated Landed Cost",default=False)

class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    y_stock_picking_id = fields.Many2one('stock.picking')
    cost_id = fields.Many2one('stock.landed.cost', 'Landed Cost',required=False)
    # value = fields.Char("Value")
    # to get the only landed cost true  by s
    product_id = fields.Many2one('product.product', 'Product', domain=[('landed_cost_ok', '=', True),('y_automated_landed_cost','=',True)])
    # to set the value by quantity overide the standerd by s

class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    picking_ids = fields.Many2many(
        'stock.picking', string='Transfers',
        copy=False, store=True)
    y_restrict_create_bool = fields.Boolean()

    @api.model
    def create(self,vals):
        res = super(LandedCost,self).create(vals)
        if res.y_restrict_create_bool == True:
            if res:
                res.compute_landed_cost()
            if res:
                svl_subtotal = sum(res.picking_ids.move_ids_without_package.stock_valuation_layer_ids.mapped('value'))
                for cost_line in res.cost_lines:
                    po_landed_cost_subtotal = sum(res.picking_ids.purchase_id.order_line.filtered(lambda x: x.product_id.product_tmpl_id == cost_line.product_id.product_tmpl_id).mapped('price_subtotal'))

                po_product_subtotal = 0
                for adjust_cost_lines in res.valuation_adjustment_lines:
                    prod_val = adjust_cost_lines.product_id
                    po_product_subtotal = po_product_subtotal + sum(res.picking_ids.purchase_id.order_line.filtered(lambda x: x.product_id.product_tmpl_id == prod_val.product_tmpl_id and x.product_id.product_tmpl_id.detailed_type == 'product').mapped('price_subtotal'))
                    if po_product_subtotal:
                        prod_subtotal = po_product_subtotal
                    else:
                        prod_subtotal = 0

                if prod_subtotal==0:
                    land_val=0
                else:
                    land_val = ((svl_subtotal * po_landed_cost_subtotal)/prod_subtotal)
        
                for rec in res.picking_ids.purchase_id.order_line:
                    cost_line_obj = res.cost_lines.filtered(lambda x:x.product_id.product_tmpl_id == rec.product_id.product_tmpl_id)
                    # if cost_line_obj:
                    #     cost_line_obj.update({'price_unit': land_val})
                    res.compute_landed_cost()
            if res:
                res.button_validate()
        return res

    def compute_landed_cost(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()
        digits = self.env['decimal.precision'].precision_get('Product Price')
        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost._get_targeted_move_ids()):
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    # print(val.purchase_id.order_line.product_id.product_tmpl_id,555555555555555555555555555555555555555)
                    # print(val.purchase_id.order_line.filtered(lambda x:x.product_id.product_tmpl_id == val_line_values.get('product_id')),11111111222222222222222222222222222222222222222)

                    # print(sum(val.purchase_id.order_line.filtered(lambda x:x.product_id.product_tmpl_id == val_line_values.get('product_id')).mapped('price_subtotal')),9999999999999999999999999999999999999999999999)

                    # print(sum(val.purchase_id.order_line.filtered(lambda x: x.product_id.product_tmpl_id == prod_val.product_tmpl_id and x.product_id.product_tmpl_id.detailed_type == 'product').mapped('price_subtotal')),333333333333333333333333333333333333333333333)
                    
                    # print(sum(val.purchase_id.order_line.filtered(lambda x: x.product_id.product_tmpl_id == cost_line.product_id.product_tmpl_id).mapped('price_subtotal')),"it is a insurance product111111111111111111111111111111111111111111111111")


                    # print(sum(val.purchase_id.order_line.filtered(lambda x:x.product_id.product_tmpl_id == prod_val.product_tmpl_id.id and x.product_id.product_tmpl_id.detailed_type == 'product').mapped('price_subtotal')),55555555555555555555555555555555555555555555555555555)
                    # cost_line.update({'price_unit': 150})

                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                total_cost += tools.float_round(former_cost, precision_digits=digits) if digits else former_cost

                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = tools.float_round(value, precision_digits=digits, rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    y_bool_field = fields.Boolean(default=False,copy=False)
    y_button_validate_bool = fields.Boolean(default=True,copy=False)
    y_post_validate_button_bools = fields.Boolean(default=False,copy=False)
    y_post_validate_button_warning = fields.Boolean(default=False,copy=False)
    y_post_validate_button_success = fields.Boolean(default=False,copy=False)
    y_button_box_landed_cost_bool = fields.Boolean(default=False,copy=False)
    y_is_post_landedcost = fields.Boolean(default=False,copy=False)
    y_landed_cost_ids = fields.One2many('stock.landed.cost.lines','y_stock_picking_id',compute="get_landed_cost_line")
    
    # @api.model
    # def create(self,vals):
    #     res = super(StockPicking,self).create(vals)
    #     for stock_picking_val in res:
    #         if stock_picking_val.origin:
    #             purchase_val = self.env['purchase.order'].search([('name','=',stock_picking_val.origin)])
    #             for purchase_order_val in purchase_val.order_line:
    #                 if purchase_order_val.product_id.y_automated_landed_cost == True:
    #                     stock_picking_val.y_post_validate_button_bools = True
    #                 else:
    #                     stock_picking_val.y_post_validate_button_bools = False
    #         else:
    #             stock_picking_val.y_post_validate_button_bools = False

    #     return res

    def button_validate(self):
        res = super(StockPicking,self).button_validate()

        for record in self:
            record.validate_lc()

       
        # for stock_picking_val in self:
        #     if stock_picking_val.origin:
        #         purchase_val = self.env['purchase.order'].search([('name','=',stock_picking_val.origin)])
        #         for purchase_order_val in purchase_val.order_line:
        #             if purchase_order_val.product_id.y_automated_landed_cost == True:
        #                 stock_picking_val.y_post_validate_button_warning = True
        #                 stock_picking_val.y_post_validate_button_bools = True
        #                 stock_picking_val.y_button_box_landed_cost_bool = True


        #             else:
        #                 stock_picking_val.y_post_validate_button_warning = False
        #                 stock_picking_val.y_post_validate_button_bools = False
        #                 stock_picking_val.y_button_box_landed_cost_bool = False
        #     else:
        #         stock_picking_val.y_post_validate_button_warning = False
        #         stock_picking_val.y_post_validate_button_bools = False

        return  res

    #if this function is not triggered then this piece of code should be added inside create method
    @api.depends('purchase_id')
    def get_landed_cost_line(self):
        for rec in self:
            if not rec.purchase_id:
                rec.y_landed_cost_ids = None
            else:
                val = rec.purchase_id.order_line.filtered(lambda x: x.product_id.detailed_type == 'service' and x.product_id.landed_cost_ok == True and x.product_id.y_automated_landed_cost == True)
                if val:
                    land_cost_vals = self.env['stock.landed.cost.lines']
                    for line in val:
                        land_cost_vals += self.env['stock.landed.cost.lines'].create({
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'account_id': line.product_id.property_account_expense_id.id,
                            'split_method': line.product_id.split_method_landed_cost,
                            'price_unit': line.product_id.standard_price
                        })
                else:
                    land_cost_vals = False

                rec.y_landed_cost_ids = land_cost_vals

    def validate_lc(self):
        self.y_is_post_landedcost = True
        if self.y_button_validate_bool:
            if not self.y_bool_field:               
                done_qty = sum(self.move_ids_without_package.move_line_ids.mapped('quantity'))
                
                # landed_cost_value = sum(self.move_ids_without_package.mapped('stock_valuation_layer_ids').value)
                # print(landed_cost_value,222222222222222222222222222222222222222222222222222222)
                if len(self.y_landed_cost_ids) and  done_qty>0 :
                    val = self.env['stock.landed.cost'].create({
                        'picking_ids':[(4, self.id)],
                        'y_restrict_create_bool':True,
                        'cost_lines':[(6, 0, self.y_landed_cost_ids.ids)]
                        })
                    val.compute_landed_cost()
                    self.y_bool_field = True
                    self.y_post_validate_button_warning = False
                    self.y_post_validate_button_success = True
    
    # def button_validate(self):
    #     res = super(StockPicking,self).button_validate()
    #     if self.y_button_validate_bool:
    #         print("insideeeeeeeeeeeeeeeeeeeeeeeee button_validate custom")
    #         if not self.y_bool_field:
               
    #             done_qty=0.0
    #             for each in self.move_ids_without_package:
    #                 for each_line in each.move_line_ids:
    #                     done_qty+= each_line.quantity


    #             print(self.move_ids_without_package.stock_valuation_layer_ids,333333333333333333333333333333)
                
    #             if len(self.y_landed_cost_ids) and  done_qty>0 :
    #                 # print("13.0.0.213.0.0.2",self.y_landed_cost_ids.ids)

    #                 self.env['stock.landed.cost'].create({
    #                     'picking_ids':[(4, self.id)],
    #                     'cost_lines':[(6, 0, self.y_landed_cost_ids.ids)]
    #                     })

    #                 self.y_bool_field = True
    #     return res


    def view_landed_cost_tree(self):
        self.ensure_one()
        picking_ids=[]
        action = self.env.ref('stock_landed_costs.view_stock_landed_cost_tree').read()[:1]
        for lines in self.y_landed_cost_ids:
            picking_ids = [(4, picking_ids.id, None) for picking_ids in lines.y_stock_picking_id]
        tree_view = self.env.ref('stock_landed_costs.view_stock_landed_cost_tree')
        view_id = self.env.ref('stock_landed_costs.view_stock_landed_cost_form')

        return {
            'name': _('Landed Cost'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'stock.landed.cost',
            'domain': [('picking_ids', 'in', self.ids)],
            'view_id': view_id.id,
            'views': [(tree_view.id, 'tree'),(view_id.id, 'form')],
            'type': 'ir.actions.act_window',

            }

# class StockBackOrderConfirmation(models.TransientModel):
#     _inherit = "stock.backorder.confirmation"

#     def process(self):
#         res = super(StockBackOrderConfirmation,self).process()
#         print(self._context,111111111111111111111111111111111111111111111111)
#         val = self.env['stock.picking'].browse(self._context.get('button_validate_picking_ids')[0])

#         print(val,2222222222222222222222222222222222222222222222)
        


       
#         if len(val.y_landed_cost_ids) :
#             print(val.y_landed_cost_ids.ids,"PRixgen 111111111111111111111111111111111111111111111111111")
#             self.env['stock.landed.cost'].create({
#                 'picking_ids':[(4, val.id)],
#                 'cost_lines':[(6, 0, val.y_landed_cost_ids.ids)]
#                 })

#             val.y_bool_field = True
        
#         return res



class StockValuationAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    y_remaining_qty = fields.Float(string="Remaining Qty" ,related='move_id.stock_valuation_layer_ids.remaining_qty')
    y_calculated_landed_cost = fields.Float(string="Calculated Landed Cost",compute="_compute_clc_landed_cost")

    @api.depends('y_remaining_qty','additional_landed_cost','quantity')
    def _compute_clc_landed_cost(self):
        for rec in self:
            if rec.quantity != 0:
                rec.y_calculated_landed_cost = (rec.y_remaining_qty * rec.additional_landed_cost) / rec.quantity


    @api.depends('move_id')
    def _compute_remaining_qty(self):
        for rec in self:
            rec.y_remaining_qty = sum(self.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))


class Stockmove(models.Model):
    _inherit = "stock.move"

    y_button_validate_bool = fields.Boolean(default=False,compute="get_y_button_validate_bool")
    y_quantity_done = fields.Float(store=True)

    @api.depends('y_quantity_done','product_uom_qty')
    def get_y_button_validate_bool(self):
        for rec in self:
            if rec:
                if rec.y_quantity_done and rec.product_uom_qty:
                    if rec.y_quantity_done == rec.product_uom_qty:
                        rec.y_button_validate_bool = True
                    else:
                        rec.y_button_validate_bool = False
                else:
                    rec.y_button_validate_bool = False
            else:
                rec.y_button_validate_bool = False
