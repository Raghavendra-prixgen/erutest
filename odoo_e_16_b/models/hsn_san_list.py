from odoo import models, fields, api, _,exceptions



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # supplier_taxes_id = fields.Many2many('account.tax', 'product_supplier_taxes_rel', 'prod_id', 'tax_id', string='Vendor Taxes', help='Default taxes used when buying the product.',
    #     default=lambda self: self.env.company.account_purchase_tax_id)

    def button_update_hsn_sac_code(self):
        tree_view_id = self.env.ref('odoo_e_16_b.view_hsn_san_list_tree_update_hsn_code').id
        return {
            'name': 'HSN List',
            'view_mode': 'tree',
            'views': [[tree_view_id, 'tree']],
            'res_model': 'hsn.san.list',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':dict(default_product_id=self.id,create=False,edit=False)
            }

class ProductProduct(models.Model):
    _inherit = 'product.product'


    def button_update_hsn_sac_code(self):
        tree_view_id = self.env.ref('odoo_e_16_b.view_hsn_san_list_tree_update_hsn_code').id
        return {
            'name': 'HSN List',
            'view_mode': 'tree',
            'views': [[tree_view_id, 'tree']],
            'res_model': 'hsn.san.list',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':dict(default_product_id=self.product_tmpl_id.id,create=False,edit=False)
            }
    

class HsnSanList(models.Model):
    _name = 'hsn.san.list'
    _rec_name = 'y_name'

    y_name = fields.Char(string="Name")
    y_short_description = fields.Char(string="Short Description")
    y_long_description = fields.Char(string="Long Description")
    y_customer_tax_ids = fields.Many2many('account.tax','account_tax_customer_tax_rel', domain=[('type_tax_use', '=', 'sale')],string="Customer Tax")
    y_vendor_tax_ids = fields.Many2many('account.tax',domain=[('type_tax_use', '=', 'purchase')],string="Vendor Tax")
    y_product_id = fields.Many2one('product.template',string="Product")


    def update_hsn_sac_code(self):
        for hsc_line in self:
            product_id = hsc_line.env['product.template']
            if hsc_line._context.get('params'):
                if hsc_line._context.get('model') == 'product.product':
                    product_id = hsc_line.env['product.product'].browse(hsc_line._context.get('default_product_id')).product_tmpl_id

            if len(self) == 1:
                if not product_id:
                    product_id = hsc_line.env['product.template'].browse(hsc_line._context.get('default_product_id'))
                customer_tax_ids = product_id.taxes_id + hsc_line.y_customer_tax_ids
                vendor_tax_ids = product_id.supplier_taxes_id + hsc_line.y_vendor_tax_ids
                product_id.write({'l10n_in_hsn_code':hsc_line.y_name,
                                           'l10n_in_hsn_description':hsc_line.y_short_description,
                                           'taxes_id':[(6,0,customer_tax_ids.ids)],
                                           'supplier_taxes_id':[(6,0,vendor_tax_ids.ids)]})

                
              