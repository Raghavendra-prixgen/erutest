# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    code = fields.Char('Short Name', required=True, size=10, help="Short name used to identify your warehouse")

class ItemGroup(models.Model):
    _name = "item.group"
    _description = "Item Group"
    _rec_name = 'y_name'
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    y_name = fields.Char()
    y_code = fields.Char()
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)

    @api.constrains('y_code','company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['item.group'].search([('y_code','=',rec.y_code),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))



class ProductGroup1(models.Model):
    _name = "product.group.1"
    _description = "Product Group 1"
    _rec_name = 'y_name'
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    y_name = fields.Char()
    y_code = fields.Char()
    y_product_category_id = fields.Many2one('product.category')
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)

    @api.constrains('y_code','y_company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['product.group.1'].search([('y_code','=',rec.y_code),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))


class ProductGroup2(models.Model):
    _name = "product.group.2"
    _description = "Product Group 2"
    _rec_name = 'y_name'
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    y_name = fields.Char()
    y_code = fields.Char()
    y_product_group_1 = fields.Many2one('product.group.1')
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)

    @api.constrains('y_code','y_company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['product.group.2'].search([('y_code','=',rec.y_code),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))


class ProductGroup3(models.Model):
    _name = "product.group.3"
    _description = "Product Group 3"
    _rec_name = 'y_name'
    # _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    y_name = fields.Char()
    y_code = fields.Char()
    y_product_group_2 = fields.Many2one('product.group.2')
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    active = fields.Boolean(default=True)
    
    @api.constrains('y_code','y_company_id')
    def check_item_group_code(self):
        for rec in self:
            docs=rec.env['product.group.3'].search([('y_code','=',rec.y_code),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""code already exists!"""))



class ProductTemplate(models.Model):
    _inherit = "product.template"

    y_item_group = fields.Many2one('item.group', ondelete='restrict')
    y_product_group_1 = fields.Many2one('product.group.1', domain="[('y_product_category_id', '=', categ_id)]", ondelete='restrict')
    y_product_group_2 = fields.Many2one('product.group.2', domain="[('y_product_group_1', '=', y_product_group_1)]", ondelete='restrict')
    y_product_group_3 = fields.Many2one('product.group.3', domain="[('y_product_group_2', '=', y_product_group_2)]", ondelete='restrict')


class ProductProduct(models.Model):
    _inherit = "product.product"

    y_item_group = fields.Many2one(related='product_tmpl_id.y_item_group', store=True)
    y_product_group_1 = fields.Many2one(related='product_tmpl_id.y_product_group_1',store=True)
    y_product_group_2 = fields.Many2one(related='product_tmpl_id.y_product_group_2',store=True)
    y_product_group_3 = fields.Many2one(related='product_tmpl_id.y_product_group_3',store=True)

class StockQuant(models.Model):
    _inherit = "stock.quant"

    y_product_category_id = fields.Many2one('product.category',related='product_id.product_tmpl_id.categ_id', store=True)
    y_item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.y_item_group', store=True)
    y_product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.y_product_group_1',store=True)
    y_product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.y_product_group_2',store=True)
    y_product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.y_product_group_3',store=True)
    
    @api.model
    def _get_inventory_fields_write(self):            
        res = super(StockQuant,self)._get_inventory_fields_write()
        return res + ['y_product_category_id', 'y_item_group', 'y_product_group_1','y_product_group_2','y_product_group_3']
  
class StockMove(models.Model):
    _inherit = "stock.move"

    y_product_category_id = fields.Many2one('product.category',related='product_id.product_tmpl_id.categ_id', store=True)
    y_item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.y_item_group', store=True)
    y_product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.y_product_group_1',store=True)
    y_product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.y_product_group_2',store=True)
    y_product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.y_product_group_3',store=True)


class StockMove(models.Model):
    _inherit = "stock.move.line"

    y_product_category_id = fields.Many2one('product.category',related='product_id.product_tmpl_id.categ_id', store=True,)
    y_item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.y_item_group', store=True)
    y_product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.y_product_group_1',store=True)
    y_product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.y_product_group_2',store=True)
    y_product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.y_product_group_3',store=True)