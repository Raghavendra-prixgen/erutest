from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    y_doc_type_ids = fields.Many2many('purchase.doc.type', string="Document Type")