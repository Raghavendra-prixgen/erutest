from urllib import request
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import json


class StockMoveReport(models.Model):
    _inherit = 'stock.move'

    y_stock_product_code = fields.Char(related="product_id.default_code",string="Product Code")
    y_mrp_fg_product_code = fields.Char(related="y_mrp_fg_product_id.default_code",string="FG Code")
    y_mrp_parent_state = fields.Selection(related="raw_material_production_id.state")
    y_mrp_fg_product_id = fields.Many2one(related="raw_material_production_id.product_id",string="FG Product")
    y_mrp_due_date = fields.Datetime(related="raw_material_production_id.date_start")
    y_remaining_quantity = fields.Float(string="Remaining Qty",compute="get_remianing_qty")
    y_mrp_sale_order_number = fields.Char(related="raw_material_production_id.y_so_origin",string="Sale Order")

    def get_remianing_qty(self):
        for rec in self:
            if rec:
                rec.y_remaining_quantity = rec.product_uom_qty - rec.quantity
            else:
                rec.y_remaining_quantity = 0

class ProductTemplateStockMoveReport(models.Model):
    _inherit = "product.template"

    def action_stock_move_report(self):
        for rec in self:
            tree_view_id = self.env.ref('odoo_e_19_b.stock_move_report_inherit_tree_view').id
            return {
            'name': 'Stock Move',
            'view_mode': 'tree',
            'views': [[tree_view_id, 'tree']],
            'res_model': 'stock.move',
            'type': 'ir.actions.act_window',
            'target': 'fullscreen',
            'domain': [('y_mrp_parent_state','in',('confirmed','progress','to_close')),('product_id','=',rec.product_variant_id.id)],
            "context":{},
            }