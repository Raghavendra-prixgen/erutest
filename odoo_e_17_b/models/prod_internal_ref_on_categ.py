# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductCategory(models.Model):
    _inherit = "product.category"

    y_internal_reference_sequence_id = fields.Many2one('ir.sequence',string="Internal Reference Sequence")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    y_internal_reference_sequence = fields.Boolean(compute='compute_internal_reference',string="Internal Reference Sequence",store=True)
    default_code = fields.Char(tracking=True)
    list_price = fields.Float(tracking=True)
    standard_price = fields.Float(tracking=True)
    categ_id = fields.Many2one(tracking=True)
    default_code = fields.Char('Internal Reference', compute=False,inverse='_set_default_code', store=True)

    def _prepare_variant_values(self, combination):
        res = super()._prepare_variant_values(combination)
        res['default_code'] = self.default_code
        return res

    @api.depends('categ_id')
    def compute_internal_reference(self):
        for line in self:
            if line.categ_id.y_internal_reference_sequence_id:
                line.y_internal_reference_sequence = True
            else:
                line.y_internal_reference_sequence = False

    @api.model
    def create(self,vals):
        sequence = self.env['product.category'].browse(vals.get('categ_id')).y_internal_reference_sequence_id
        if sequence:
            vals['default_code'] = sequence.next_by_id()
        
        return super(ProductTemplate,self).create(vals)