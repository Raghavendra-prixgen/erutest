# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,tools
from odoo.exceptions import ValidationError
import pdb
    
class InvBalSumWiz(models.Model):
    _name = 'inv.bal.sum.report.view'
    _auto = False

    _description = 'Inventory Summary'
    
    purchase_qty = fields.Float('Purchase(Qty)')
    purchase_value = fields.Float('Purchase(Value)')
    purchase_return_qty = fields.Float('Purchase Return(Qty)')
    purchase_return_value = fields.Float('Purchase Return(Value)')
    sale_qty = fields.Float('Sale(Qty)')
    sale_value = fields.Float('Sale(Value)')
    sale_return_qty = fields.Float('Sale Return(Qty)')
    sale_return_value = fields.Float('Sale Return(Value)')
    production_qty = fields.Float('Production(Qty)')
    production_value = fields.Float('Production(Value)')
    consumption_qty = fields.Float('Consumption(Qty)')
    consumption_value = fields.Float('Consumption(Value)')
    positive_adjustment_qty = fields.Float('Positive Adjustment(Qty)')
    positive_adjustment_value = fields.Float('Positive Adjustment(Value)')
    negative_adjustment_qty = fields.Float('Negative Adjustment(Qty)')
    negative_adjustment_value = fields.Float('Negative Adjustment(Value)')
    default_code = fields.Char(string="Code")
    product_id = fields.Many2one('product.product',string="Product")
    categ_id = fields.Many2one('product.category',string="Product Category")
    uom_id = fields.Many2one('uom.uom',string="UOM")
    company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id.id)
    opening_stock = fields.Float('Opening(Qty)')
    opening_value = fields.Float('Opening(Value)')
    closing_stock = fields.Float('Closing(Qty)')
    closing_value = fields.Float('Closing(Value)')
    
    
class InvBalSumWiz(models.TransientModel):
    _name = 'inv.bal.sum.wiz'
    _description = 'Inventory Summary Wizard'

    y_open_date = fields.Date(string='Start Date')
    y_close_date = fields.Date(string='End Date')
    y_company_ids = fields.Many2many('res.company',string='Companies')
    # y_product_group_id_1 = fields.Many2one('product.group.1',string='Product Group 1')
    # y_product_group_id_2 = fields.Many2one('product.group.2',string='Product Group 2')
    # y_product_group_id_3 = fields.Many2one('product.group.3',string='Product Group 3')
    # # y_product_category_id = fields.Many2one('product.category',string="Product Category")
    # y_categ_id = fields.Many2many('product.category', string="Product Category")
    
    @api.onchange('y_close_date')
    def _onchange_y_close_date(self):
        if self.y_close_date < self.y_open_date:
            raise ValidationError(_("""End Date should not be less than Start Date"""))   
    
    # warehouse_ids = fields.Many2many('stock.warehouse')
    # categ_ids = fields.Many2one('product.category')
    # product_categ_ids = fields.Many2many('product.category')
    
    
    # @api.onchange('y_company_ids')
    # def _onchange_y_company_ids(self):
    #     if self.y_company_ids:
    #         # Fetch the warehouses related to the selected companies
    #         warehouses = self.env['stock.warehouse'].search([
    #             ('company_id', 'in', self.y_company_ids.ids)
    #         ])
    #         self.warehouse_ids = [(6, 0, warehouses.ids)]
    #     else:
    #         self.warehouse_ids = [(5,)]
              
    
    
    
    def action_open_detailed_report(self):
        open_date = str(self.y_open_date) + ' 00:00:00'
        close_date = str(self.y_close_date) + ' 23:59:59'
        company = self.env.company.id
        companies = str(tuple(self.y_company_ids.ids)+(0,))

        # warehouse_name = str(tuple(self.warehouse_ids.mapped('code'))+())
        # warehouses = str(tuple(self.warehouse_ids.ids)+(0,))
        # categ = str(tuple(self.product_categ_ids.ids)+(0,))
        
        tools.drop_view_if_exists(self._cr, 'inv_bal_sum_report_view')

        self._cr.execute("""CREATE OR REPLACE VIEW inv_bal_sum_report_view AS ( 
                          SELECT distinct Row_Number() OVER() ID, result.*
                          from (SELECT distinct pp.id as product_id,svl.company_id,pt.uom_id,pt.categ_id,pp.default_code,
                          opening_stock.opening_stock,opening_value.opening_value,
                          stock_increase.stock_increase,increase_value.increase_value,
                          stock_decrease.stock_decrease,decrease_value.decrease_value,
                          (coalesce((opening_stock.opening_stock),0) + (coalesce((stock_increase.stock_increase),0) + (coalesce((stock_decrease.stock_decrease),0)))) as closing_stock,
                          (coalesce((opening_value.opening_value),0) + (coalesce((increase_value.increase_value),0) + (coalesce((decrease_value.decrease_value),0)))) as closing_value,
                          purchase_qty.purchase_qty,
                          purchase_value.purchase_value,
                          purchase_return_qty.purchase_return_qty,
                          purchase_return_value.purchase_return_value,
                          sale_qty.sale_qty,
                          sale_value.sale_value,
                          sale_return_qty.sale_return_qty,
                          sale_return_value.sale_return_value,
                          production_qty.production_qty,
                          production_value.production_value,
                          consumption_qty.consumption_qty,
                          consumption_value.consumption_value,
                          positive_adjustment_qty.positive_adjustment_qty,
                          positive_adjustment_value.positive_adjustment_value,
                          negative_adjustment_qty.negative_adjustment_qty,
                          negative_adjustment_value.negative_adjustment_value
                          from stock_valuation_layer svl
                          LEFT JOIN product_product pp on svl.product_id = pp.id
                          LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id

                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity)as opening_stock FROM stock_valuation_layer as svl join product_product pp on pp.id = svl.product_id join product_template pt on pt.id = pp.product_tmpl_id WHERE svl.create_date < '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' GROUP BY product_id)opening_stock on opening_stock.product_id = svl.product_id

                          LEFT JOIN(SELECT svl.product_id,SUM(value) as opening_value FROM stock_valuation_layer as svl join product_product pp on pp.id = svl.product_id join product_template pt on pt.id = pp.product_tmpl_id WHERE svl.create_date < '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' GROUP BY product_id)opening_value on opening_value.product_id = svl.product_id 

                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as stock_increase FROM stock_valuation_layer as svl join product_product pp on pp.id = svl.product_id join product_template pt on pt.id = pp.product_tmpl_id WHERE svl.create_date >= '%s' AND svl.create_date <= '%s' AND (svl.quantity > 0)
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' GROUP BY product_id)stock_increase on stock_increase.product_id = svl.product_id 

                          LEFT JOIN(SELECT svl.product_id,SUM(value) as increase_value FROM stock_valuation_layer as svl join product_product pp on pp.id = svl.product_id join product_template pt on pt.id = pp.product_tmpl_id WHERE svl.create_date >= '%s' AND svl.create_date <= '%s' AND ((svl.quantity > 0) or (svl.quantity = 0 and svl.value > 0))
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' GROUP BY product_id)increase_value on increase_value.product_id = svl.product_id

                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as stock_decrease FROM stock_valuation_layer as svl join product_product pp on pp.id = svl.product_id join product_template pt on pt.id = pp.product_tmpl_id WHERE svl.create_date >= '%s' AND svl.create_date <= '%s' AND (svl.quantity < 0)
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' GROUP BY product_id)stock_decrease on stock_decrease.product_id = svl.product_id

                          LEFT JOIN(SELECT svl.product_id,SUM(value) as decrease_value FROM stock_valuation_layer as svl join product_product pp on pp.id = svl.product_id join product_template pt on pt.id = pp.product_tmpl_id WHERE svl.create_date >= '%s' AND svl.create_date <= '%s' AND ((svl.quantity < 0) or (svl.quantity = 0 and svl.value < 0))
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' GROUP BY product_id)decrease_value on decrease_value.product_id = svl.product_id


                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as purchase_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'supplier' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)purchase_qty on purchase_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as purchase_value
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'supplier' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)purchase_value on purchase_value.product_id = svl.product_id
                          
                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as purchase_return_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'supplier'
                                    GROUP BY svl.product_id)purchase_return_qty on purchase_return_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as purchase_return_value 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'supplier'
                                    GROUP BY svl.product_id)purchase_return_value on purchase_return_value.product_id = svl.product_id


                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as sale_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'customer'
                                    GROUP BY svl.product_id)sale_qty on sale_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as sale_value
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'customer'
                                    GROUP BY svl.product_id)sale_value on sale_value.product_id = svl.product_id
                          
                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as sale_return_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'customer' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)sale_return_qty on sale_return_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as sale_return_value 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'customer' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)sale_return_value on sale_return_value.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as production_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'production' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)production_qty on production_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as production_value
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'production' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)production_value on production_value.product_id = svl.product_id
                          
                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as consumption_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'production'
                                    GROUP BY svl.product_id)consumption_qty on consumption_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as consumption_value 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'production'
                                    GROUP BY svl.product_id)consumption_value on consumption_value.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as positive_adjustment_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'inventory' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)positive_adjustment_qty on positive_adjustment_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as positive_adjustment_value
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'inventory' and dest_sl.usage = 'internal'
                                    GROUP BY svl.product_id)positive_adjustment_value on positive_adjustment_value.product_id = svl.product_id
                          
                          
                          LEFT JOIN(SELECT svl.product_id,SUM(svl.quantity) as negative_adjustment_qty 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'inventory'
                                    GROUP BY svl.product_id)negative_adjustment_qty on negative_adjustment_qty.product_id = svl.product_id

                          
                          LEFT JOIN(SELECT svl.product_id,SUM(value) as negative_adjustment_value 
                                    FROM stock_valuation_layer as svl 
                                    join product_product pp on pp.id = svl.product_id 
                                    join product_template pt on pt.id = pp.product_tmpl_id 
                                    join stock_move source_sm on source_sm.id = svl.stock_move_id 
                                    join stock_location source_sl on source_sl.id = source_sm.location_id  
                                    join stock_move dest_sm on dest_sm.id = svl.stock_move_id 
                                    join stock_location dest_sl on dest_sl.id = dest_sm.location_dest_id  
                                    WHERE svl.create_date >= '%s' AND svl.create_date <= '%s'
                                    AND svl.company_id in %s AND pt.detailed_type = 'product' and source_sl.usage = 'internal' and dest_sl.usage = 'inventory'
                                    GROUP BY svl.product_id)negative_adjustment_value on negative_adjustment_value.product_id = svl.product_id

                          where pt.detailed_type = 'product' and (svl.company_id in %s and pp.active = true)
                          order by pp.id asc)result)
                          """%(open_date,companies,
                              open_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,

                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              open_date,close_date,companies,
                              
                              companies))


        tree_view_id = self.env.ref('odoo_e_49.tree_view_inventory_balance_detailed_summmary').id

        return {
            'name': 'Inventory Detailed Summary ({} To {})'.format(self.y_open_date,self.y_close_date),
            'view_mode': 'tree,pivot',
            'views': [[tree_view_id, 'tree']],
            'res_model': 'inv.bal.sum.report.view',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('company_id','in',self.y_company_ids.ids)]
            }


