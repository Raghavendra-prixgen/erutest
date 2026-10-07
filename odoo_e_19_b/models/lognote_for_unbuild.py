import json
import datetime
import math
import re
import warnings

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import OrderedSet, format_date

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

class LogMrpProduction(models.Model):
    _name = 'mrp.unbuild'
    _inherit = ['mrp.unbuild','mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one(tracking=True)
    bom_id = fields.Many2one(tracking=True)
    product_qty = fields.Float(tracking=True)
    # analytic_account = fields.Many2one(tracking=True )
    # analytic_tags = fields.Many2many(tracking=True )
    location_id = fields.Many2one(tracking=True)
    location_dest_id = fields.Many2one(tracking=True)

    