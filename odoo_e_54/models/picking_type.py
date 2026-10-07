# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    y_consumable = fields.Boolean('Consumable')
    y_product_category = fields.Many2many('product.category',string='Product Category')