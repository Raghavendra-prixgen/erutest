# -*- coding: utf-8 -*-

from odoo import models, api, fields,_

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    active = fields.Boolean(default=True)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    active = fields.Boolean(default=True)

class UomCategory(models.Model):
    _inherit = 'uom.category'

    active = fields.Boolean(default=True)
    
class ResCompany(models.Model):
    _inherit = 'res.company'

    active = fields.Boolean(default=True)