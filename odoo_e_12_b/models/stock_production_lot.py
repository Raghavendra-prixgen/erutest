from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    y_vendor = fields.Many2one('res.partner',string="Vendor",store=True)
    y_product_category = fields.Many2one(related='product_id.categ_id',string="Product Category",store=True)