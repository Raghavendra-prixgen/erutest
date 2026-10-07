# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class CustomSaleDocType(models.Model):
    _name = 'sale.doc.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = 'Sale Order Document Type'
    _rec_name = 'y_name'

    active = fields.Boolean(default=True)
    y_name = fields.Char(string='Name')
    y_description = fields.Char(strinng='Description')
    y_sequence_id = fields.Many2one('ir.sequence' ,string='Sequence')
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    # is_approval_required = fields.Boolean(default=True) #comment,,,,,,,,,,
    
    @api.constrains('y_name','y_company_id')
    def check_document_name(self):
        for rec in self:
            docs=rec.env['sale.doc.type'].search([('y_name','=',rec.y_name),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""name already exists!"""))


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    # y_revision_count = fields.Integer(default=0,copy=False)
    # y_origin_order_id = fields.Many2one('sale.order',copy=False)
    # y_restore_order_id = fields.Many2one('sale.order',copy=False)
    # y_revision_order_ids = fields.One2many('sale.order', 'y_origin_order_id')
    y_doc_type_id = fields.Many2one('sale.doc.type', string="Document Type", ondelete="restrict",  store=True,copy=False)
    # y_quotation_number = fields.Char(copy=False)
    # state = fields.Selection(selection_add=[('revn','Revision')])

    @api.onchange('partner_id')
    def get_document_type(self):
        for rec in self:
            if rec.partner_id:
                rec.y_doc_type_id = rec.partner_id.y_sale_doc_type_id
            else:
                rec.y_doc_type_id = False

    def action_confirm(self):
        for rec in self:
            if not rec.y_doc_type_id:
                raise ValidationError(_("""Mapping Document type is required to confirm a Sales Quotation"""))
            # if rec.y_restore_order_id:
            #     rec.y_quotation_number = rec.y_restore_order_id.name
            # else:
            #     rec.y_quotation_number = rec.name
            #     rec.y_revision_count += 1
                
            #     # rec.create_revision(rec.name,'draft')

            rec.name = rec.y_doc_type_id.y_sequence_id.next_by_id()
        return super(CustomSaleOrder, self).action_confirm()

    # def unlink(self):
    #     for rec in self:
    #         if rec.y_origin_order_id:
    #             raise ValidationError(_("""Can not delete Sale Order Revision"""))
    #     return super(CustomSaleOrder, self).unlink()

    # def restore_revision(self):
    #     if self.y_origin_order_id.state != 'draft':
    #         raise ValidationError(_("""Can only restore to a draft Quotation"""))
    #     self.state = 'draft'
    #     old_origin = self.y_origin_order_id
    #     self.y_origin_order_id.create_revisions()
    #     new_origin = self.copy({
    #         'name':self.y_origin_order_id.name,
    #         'y_revision_count':self.y_origin_order_id.y_revision_count,
    #         'y_revision_order_ids':[(6, 0, self.y_origin_order_id.y_revision_order_ids.ids)],
    #         'y_restore_order_id':self.id
    #     })
    #     old_origin.unlink()
    #     return {
    #         'name': new_origin.name,
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'sale.order',
    #         'res_id': new_origin.id
    #     }
    
    # def create_revision(self,name,state):
    #     self.copy({
    #         'name': name,
    #         'state': state,
    #         'y_origin_order_id': self.id,
    #         'date_order':self.date_order,
    #         'validity_date':self.validity_date,
    #         })
        
    #     date_validity = self._default_validity_date()
    #     self.write({'date_order':fields.Datetime.now(),
    #                 'validity_date':date_validity})

    # def create_revisions(self):
    #     for rec in self:
    #         if rec.y_origin_order_id:
    #             raise ValidationError(_("""Can not revise Revisions"""))
    #         if rec.state in ("sale","done","cancel"):
    #             raise ValidationError(_("""Only draft Quotations can be revised"""))
    #         rec.y_revision_count += 1
    #         rec.create_revision("{}-{}".format(rec.name,rec.y_revision_count),'revn')
    
    # def view_previous_versions(self):
    #     return {
    #         'name': 'Quotation',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'sale.order',
    #         'domain': [('y_origin_order_id', '=', self.id)],
    #         'context': dict(self._context, create=False, edit=False)
    #     }
    
    # def action_quotation_sent(self):
    #     for order in self:
    #         if order.y_origin_order_id:
    #             raise ValidationError(_("""Can not mark a Revision and sent"""))
    #     return super(CustomSaleOrder, self).action_quotation_sent()
    
    def action_draft(self):
        for rec in self:
            if rec.state in ('sale','done','cancel'):
                raise ValidationError(_("""Invalid Action"""))
            else:
                continue

class CustomSalePaymentLink(models.TransientModel):
    _inherit = "payment.link.wizard"

    # @api.model
    # def default_get(self, fields):
    #     res = super(CustomSalePaymentLink, self).default_get(fields)
    #     if res['res_id'] and res['res_model'] == 'sale.order':
    #         record = self.env[res['res_model']].browse(res['res_id'])
    #         if record.y_origin_order_id:
    #             raise ValidationError(_("""Can not Create Payment Link for a Revision"""))
    #     return res

class CustomPortalMixin(models.AbstractModel):
    _inherit = "portal.mixin"

    # @api.model
    # def action_share(self):
    #     if self.env.context['active_model'] == 'sale.order':
    #         if self.env['sale.order'].browse(self.env.context['active_id']).y_origin_order_id:
    #             raise ValidationError(_("""Can not Share a Revision"""))
    #     return super(CustomPortalMixin, self).action_share()




class CustomSaleReport(models.Model):
    _inherit = "sale.report"

    #comment..................L............

    # item_group = fields.Many2one('item.group')
    # product_group_1 = fields.Many2one('product.group.1')
    # product_group_2 = fields.Many2one('product.group.2')
    # product_group_3 = fields.Many2one('product.group.3')

    # def _select_additional_fields(self):
    #     res = super()._select_additional_fields()
    #     res['item_group'] = "t.item_group"
    #     res.update({
    #         'item_group': 't.item_group',
    #         'product_group_1': 't.product_group_1',
    #         'product_group_2': 't.product_group_2',
    #         'product_group_3': 't.product_group_3',
    #     })
    #     return res

    # def _group_by_sale(self):
    #     res = super()._group_by_sale()
    #     res += """,
    #         t.item_group,
    #         t.product_group_1,
    #         t.product_group_2,
    #         t.product_group_3
    #         """
    #     return res



class CustomResPartnerNew(models.Model):
    _inherit = "res.partner"


    y_sale_doc_type_id = fields.Many2one('sale.doc.type', string="Document Type")
