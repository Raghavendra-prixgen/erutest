import calendar
from collections import defaultdict, OrderedDict
from datetime import timedelta
from odoo import _, api, fields, models

class Logforrulesproducttemplate(models.Model):
    _name = "product.template"
    _inherit = ['product.template','mail.thread', 'mail.activity.mixin']

    detailed_type = fields.Selection(tracking=True)
    invoice_policy = fields.Selection(tracking=True)
    list_price = fields.Float(tracking=True)
    tic_category_id = fields.Many2one(tracking=True)
    standard_price = fields.Float(tracking=True)
    default_code = fields.Char(tracking=True)
    l10n_in_hsn_description = fields.Char(tracking=True)
    barcode = fields.Char(tracking=True)
    categ_id = fields.Many2one(tracking=True)
    

class Logforrulespricelist(models.Model):
    _name = "product.pricelist"
    _inherit = ['product.pricelist','mail.thread', 'mail.activity.mixin']

    name = fields.Char(translate=True)
    currency_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)

    
class Logforrulesdeliverycarrier(models.Model):
    _name = "delivery.carrier"
    _inherit = ['delivery.carrier','mail.thread', 'mail.activity.mixin']

    name = fields.Char(translate=True)
    delivery_type = fields.Selection(tracking=True)
    company_id = fields.Many2one(tracking=True)
    free_over = fields.Boolean(tracking=True)
    product_id = fields.Many2one(tracking=True)
    margin = fields.Float(tracking=True)
    fixed_price = fields.Float(tracking=True)
    zip_from = fields.Char(tracking=True)
    zip_to = fields.Char(tracking=True)


class Logforrulesuom(models.Model):
    _name = "uom.uom"
    _inherit = ['uom.uom','mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    category_id = fields.Many2one(tracking=True)
    uom_type = fields.Selection(tracking=True)
    l10n_in_code = fields.Char(tracking=True)
    rounding = fields.Float(tracking=True)
    active = fields.Boolean(tracking=True)


class Logforrulesuomcategory(models.Model):
    _name = "uom.category"
    _inherit = ['uom.category','mail.thread', 'mail.activity.mixin']

    name = fields.Char(translate=True)


class Logforrulesuomcategory(models.Model):
    _name = "mail.activity.type"
    _inherit = ['mail.activity.type','mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    category = fields.Selection(tracking=True)
    default_user_id = fields.Many2one(tracking=True)
    default_note = fields.Html(tracking=True)
    res_model = fields.Selection(tracking=True)
    summary = fields.Char(tracking=True)
    icon = fields.Char(tracking=True)
    decoration_type = fields.Selection(tracking=True)    
    chaining_type = fields.Selection(tracking=True)
    delay_count = fields.Integer(tracking=True)
    delay_unit = fields.Selection(tracking=True)
    delay_label = fields.Char(tracking=True)
    delay_from = fields.Selection(tracking=True)
