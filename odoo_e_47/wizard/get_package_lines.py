from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import datetime, timedelta,date

class GetPackagelines(models.TransientModel):
    _name = 'get.package.line'
    _description = 'get.package.line'

    y_package_id = fields.Many2one('stock.quant.package')
    y_partner_id = fields.Many2one('res.partner',string="Customer", related='y_package_id.y_partner_id')
    is_stock_picking = fields.Boolean(string="Shipment")
    is_stock_move_line = fields.Boolean(string="Shipment Line")
    y_picking_ids = fields.Many2many('stock.picking',required=True,store=True,string="Shipment",domain="[('partner_id', '=', y_partner_id),('state','=','assigned'),('picking_type_id.code', '=', 'outgoing')]")
    y_stock_move_line_ids = fields.Many2many('stock.move.line',required=True,store=True,string="Shipment Line",domain="[('picking_partner_id', '=', y_partner_id),('state','=','assigned'),('picking_type_id.code', '=', 'outgoing')]" )

    def action_confirm(self):
        for rec in self:
            if rec.y_package_id:
                if  rec.y_stock_move_line_ids:
                    rec.y_stock_move_line_ids.result_package_id = rec.y_package_id.id
                else:
                    rec.y_picking_ids.move_line_ids_without_package.result_package_id = rec.y_package_id.id

