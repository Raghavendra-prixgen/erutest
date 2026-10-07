from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS
from odoo.tools import float_round

from collections import defaultdict


class LogsMrpBom(models.Model):
    _name = 'mrp.bom'
    _inherit = ['mrp.bom','mail.thread', 'mail.activity.mixin']
   

    subcontractor_ids = fields.Many2many(tracking=True)
    code = fields.Char(tracking=True)
    type = fields.Selection(tracking=True)
    product_tmpl_id = fields.Many2one(tracking=True)
    product_id = fields.Many2one(tracking=True)
    product_qty = fields.Float(tracking=True)
    ready_to_produce = fields.Selection(tracking=True)
    picking_type_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    consumption = fields.Selection(tracking=True)
    sale_orders_id = fields.Many2one('sale.order',string="Sale Order No")
