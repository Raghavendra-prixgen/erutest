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

class LogForScrap(models.Model):
    _name = 'stock.scrap'   
    _inherit = ['stock.scrap','mail.thread', 'mail.activity.mixin']

    origin = fields.Char(tracking=True)
    product_id = fields.Many2one(tracking=True)
    scrap_qty = fields.Float(tracking=True)
    location_id = fields.Many2one(tracking=True)
    scrap_location_id = fields.Many2one(tracking=True)
    