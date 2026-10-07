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
    _name = 'mrp.production'
    _description = 'Production Order'   
    _inherit = ['mrp.production','mail.thread', 'mail.activity.mixin']

    analytic_account_id = fields.Many2one(tracking=True)
    product_id = fields.Many2one(tracking=True)
    product_qty = fields.Float(tracking=True)
    qty_producing = fields.Float(tracking=True)
    date_start = fields.Datetime(tracking=True)
    bom_id = fields.Many2one(tracking=True)
   

    
    
