# -*- coding: utf-8 -*-

from odoo import models, api, fields,_
from odoo.exceptions import UserError, ValidationError


class CustomFields(models.Model):
    _inherit = 'purchase.order.line'


    @api.onchange('product_qty')
    def validate_quanatity(self):  
        for line in self.order_id.requisition_id.line_ids:
            if self.order_id.requisition_id.type_id.y_order_quantities == 'block':
                qty_val = (line.product_qty-line.qty_ordered)
                val = self.filtered(lambda x:x.product_id==line.product_id)
                if qty_val  > val.product_qty:
                    raise UserError(_("Order Quantity Exceeding Requested Quantity "))
                

    y_product_ids = fields.Many2many(
        comodel_name='product.product',
    store=True,
    )

    # compute='_compute_y_product_ids',

    # @api.depends('product_id','order_id.partner_id')
    # def _compute_y_product_ids(self):
    #     for line in self:
    #         line.y_product_ids = False
           
    @api.onchange('product_id', 'order_id.partner_id')
    def _onchange_product_ids(self):
        for line in self:
            if line.product_id.product_tmpl_id.y_product_sourcing == True:
                product_ids = self._get_product_ids(line.partner_id, line.order_id.company_id)
                if line.product_id.id not in product_ids:
                    raise ValidationError(_(""" No valid Vendor price list found for this vendor. Create a vendor price list."""))
                    
                            
    def _get_product_ids(self, partner, company):
        product_ids = []
        if partner:
            partner_id = partner.id
            query = """
                SELECT pp.id
                FROM product_product pp
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN product_supplierinfo psi ON pp.product_tmpl_id = psi.product_tmpl_id
                WHERE psi.partner_id = %s
                AND pt.purchase_ok = TRUE AND pt.y_product_sourcing = TRUE
            """
            self.env.cr.execute(query, (partner_id,))
            product_ids = [row[0] for row in self.env.cr.fetchall()]

        if not product_ids:
            company_id = company.id
            query = """
                SELECT pp.id
                FROM product_product pp
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE pt.purchase_ok = TRUE AND pt.y_product_sourcing = TRUE
                AND (pt.company_id IS NULL OR pt.company_id = CAST(%s AS INTEGER))
            """
            self.env.cr.execute(query, (company_id,))
            product_ids = [row[0] for row in self.env.cr.fetchall()]

        return product_ids



class Purchasetoleranceinventry(models.Model):
    _inherit='product.template'

    y_product_sourcing = fields.Boolean(string='Product Sourcing')


class PurchaseRequisitionType(models.Model):
    _inherit = 'purchase.requisition.type'

    y_sequence_id = fields.Many2one('ir.sequence','Purchase Request Sequence')
    y_agreement_types = fields.Selection([('purchase_request','Purchase Request'),('blanket_order','Blanket Order'),('other','Other Agreements')],string="Agreement Category")
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    y_order_quantities = fields.Selection(selection=[
            ('flexible', 'Flexible'),
            ('block','Block'),   
           
        ], string='Order Quantites',default='flexible')
    
    
    @api.constrains('y_agreement_types','company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['purchase.requisition.type'].search([('y_agreement_types','=','purchase_request'),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""Purchase Request already exists!"""))
            docs1=rec.env['purchase.requisition.type'].search([('y_agreement_types','=','blanket_order'),('company_id','=',rec.company_id.id)])
            if len(docs1) > 1:
                raise ValidationError(_("""Blanket Order already exists!"""))

    
