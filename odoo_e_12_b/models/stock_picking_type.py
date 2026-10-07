from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class StockPickingTypeInherit(models.Model):
    _inherit = "stock.picking.type"

    y_custom_sequence = fields.Many2one('ir.sequence',string='Lot sequence')
    y_sn_sequence = fields.Many2one('ir.sequence',string='Serial Number sequence')

