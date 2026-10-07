
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



#related to approval engine




class AccountTransferModel(models.Model):
    _name = "account.transfer.model"
    _inherit = ['account.transfer.model','mail.thread', 'mail.activity.mixin']


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material', readonly=False,
        domain="""[('y_is_bom_approved','=',True),
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        )
    @api.depends('product_id')
    def _compute_bom_id(self):
        res = super()._compute_bom_id()
        if self.bom_id:
            if not self.bom_id.y_is_bom_approved:
                self.bom_id = False
        return res
   

class BillOfMaterial(models.Model):
    _inherit = "mrp.bom"

    y_is_bom_approved = fields.Boolean(string="BOM Approved",copy=False,default=False,tracking=True)


    def write(self,vals):
        res = super().write(vals)
        if 'y_is_bom_approved' not in vals:
            self.write({'y_is_bom_approved':False})
        return res


    def approve_bom(self):
        for rec in self:
            rec.write({'y_is_bom_approved':True}) 


class ProductTemplate(models.Model):
    _inherit = "product.template"

    y_is_product_approved = fields.Boolean(string="Product Approved")

    def write(self,vals):
        res = super().write(vals)
        if 'y_is_product_approved' not in vals:
            self.write({'y_is_product_approved':False})
        return res

    def approve_product(self):
        for rec in self:
            rec.write({'y_is_product_approved':True}) 
    #need to put domain for product which are approved

class ProductCategory(models.Model):
    _inherit = "product.category"

    def write(self,vals):
        res = super().write(vals)
        if 'y_release' not in vals:
            self.write({'y_release':False})
        return res


    def approve_product_category(self):
        for rec in self:
            rec.write({'y_release':True}) 



class LotSerialNumber(models.Model):
    _inherit = "stock.lot"

    y_is_lot_approved = fields.Boolean(string="Lot Approved")

    
    #need to put domain for lot which are approved
    def approve_lot(self):
        for rec in self:
            rec.write({'y_is_lot_approved':True}) 


    def write(self,vals):
        res = super().write(vals)
        if 'y_is_lot_approved' not in vals:
            self.write({'y_is_lot_approved':False})
        return res





#END of approval engine Code
##################################################################################





























class AccountMove(models.Model):
    _inherit = 'account.move'
   

    def action_post(self):
        for record in self:
            if record.move_type != 'entry':
                if not record.attachment_ids:
                    raise ValidationError("Attachments are required for this record.")
        return super(AccountMove,self).action_post()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    y_l10n_in_hsn_code = fields.Char(related='product_id.l10n_in_hsn_code',string="HSN/SAC Code")


class SaleOrder(models.Model):
    _inherit = "sale.order"


    def request_for_approve(self):
        for rec in self:
            hsn_code = all(rec.order_line.mapped('y_l10n_in_hsn_code'))
            if not hsn_code:
                product_list = rec.order_line.filtered(lambda x: not x.y_l10n_in_hsn_code).mapped('product_id').mapped('name')
                raise ValidationError(_("The HSN code has not been mapped for {}.".format(product_list)))

        return super().request_for_approve()

    def action_confirm(self):
        for rec in self:
            hsn_code = all(rec.order_line.mapped('y_l10n_in_hsn_code'))
            if not hsn_code:
                product_list = rec.order_line.filtered(lambda x: not x.y_l10n_in_hsn_code).mapped('product_id').mapped('name')
                raise ValidationError(_("The HSN code has not been mapped for {}.".format(product_list)))

        return super().action_confirm()


class Purchaseorder(models.Model):
    _inherit ="purchase.order"

    def request_for_approve(self):
        for rec in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id','=',rec.id)])
            if not attachment_ids:
                raise ValidationError("Attachments are required for this record.")



        return super().request_for_approve()



            