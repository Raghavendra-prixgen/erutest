from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo import api, fields, models, _
from num2words import num2words
from calendar import monthrange
from lxml import etree
from odoo.tools import float_compare, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.exceptions import UserError, ValidationError



class PackageType(models.Model):
    _inherit = 'stock.package.type'


    y_dimension = fields.Selection(
        [('cm','cm'),
        ('mm', 'mm'),
        ('m', 'm'),
        ], default='cm', tracking=True,string='Dimension in')
    # cm centimeter
    # mm millimeter
    # m meter

    @api.depends('package_carrier_type','y_dimension')
    def _compute_length_uom_name(self):
        rec = super(PackageType, self)._compute_length_uom_name()
        for package in self:
            if package.y_dimension:
                package.length_uom_name = package.y_dimension
        return rec
