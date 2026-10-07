# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductCategory(models.Model):
    _inherit = "product.category"

    y_description = fields.Char('Description')
    y_release = fields.Boolean('Release')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_id = fields.Many2one(default=False,domain=[('y_release', '=', True)]) 

    @api.model
    def default_get(self, fields):
        result = super(ProductTemplate, self).default_get(fields)
        if result.get('categ_id') and not self.env['product.category'].search([('id','=',result.get('categ_id')),('y_release','!=',False)]):
                del result['categ_id']

        return result