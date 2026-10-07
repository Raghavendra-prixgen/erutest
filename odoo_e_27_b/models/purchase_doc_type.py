# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError




class PurchaseDocType(models.Model):
    _name = 'purchase.doc.type'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Purchase Order Document Type'
    _rec_name = 'y_name'

    active = fields.Boolean(default=True)
    y_name = fields.Char(tracking=True,string='Name')
    y_description = fields.Char(tracking=True,string='Description')
    y_sequence_id = fields.Many2one('ir.sequence',tracking=True,string='Sequence')
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1,tracking=True)
    y_product_group = fields.Many2one('product.groups',string="Purchase Group",tracking=True)

    @api.constrains('y_name','y_company_id')
    def check_document_y_name(self):
        for rec in self:
            docs = rec.env['purchase.doc.type'].search([('y_name','=',rec.y_name),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""name already exists!"""))




class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # y_quotation_list_id = fields.Many2one('purchase.order',copy=False)
    # y_revision_count = fields.Integer(default=0,copy=False)
    # y_origin_order_id = fields.Many2one('purchase.order',copy=False)
    # y_revision_order_ids = fields.One2many('purchase.order', 'y_origin_order_id')
    y_doc_type_id = fields.Many2one('purchase.doc.type', string="Document Type",copy=False,tracking=True)
    y_quotation_number = fields.Char(copy=False,string="RFQ Ref")
    y_purchase_request_number = fields.Char(copy=False,string="Purchase Request Ref",store=True)
    # state = fields.Selection(selection_add=[('revn','Revision')])






    def request_approval(self):
        pass
        
    @api.onchange('partner_id')
    def get_document_type(self):
        for rec in self:
            if rec.partner_id:
                rec.y_doc_type_id = rec.partner_id.y_purchase_doc_type_id
            else:
                rec.y_doc_type_id = False


    # @api.onchange('partner_id')
    # def _onchange_partner_id_quotation_list(self):
    #     if not self.requisition_id:
    #         res={}
    #         res['domain']={'y_quotation_list_id': [('state','in',('draft','sent','to_approve')),('partner_id','=',self.partner_id.id),('y_origin_order_id','=',False),('date_planned','!=',False)]}
    #         return res

    # @api.onchange('y_quotation_list_id')
    # def _onchange_y_quotation_list_id(self):
    #     for rec in self:
    #         if not rec.requisition_id:
    #             rec.order_line = [(6, 0, self.y_quotation_list_id.order_line.ids)]

    def button_confirm(self):
        for rec in self:
            if not rec.y_doc_type_id:
                raise ValidationError(_("""Mapping Document type is required to confirm a Purchase Quotation"""))
            # self.y_revision_count += 1
            rec.y_quotation_number = rec.name
            # rec.copy({
            #     'name': rec.name,
            #     'y_origin_order_id': rec.id
            #     })
            # rec.name = self.env['ir.sequence'].next_by_id(rec.y_doc_type_id.y_sequence_id.id)
            rec.name = rec.y_doc_type_id.y_sequence_id.next_by_id()
        return super(PurchaseOrder, self).button_confirm()

    # def unlink(self):
    #     for rec in self:
    #         if rec.y_origin_order_id:
    #             raise ValidationError(_("""Can not delete Purchase Order Revision"""))
    #     return super(PurchaseOrder, self).unlink()

    # def restore_revision(self):
    #     if self.y_origin_order_id.state != 'draft':
    #         raise ValidationError(_("""Can only restore to a draft Quotation"""))
    #     old_origin = self.y_origin_order_id
    #     self.y_origin_order_id.create_revisions()
    #     new_origin = self.copy({
    #         'name':self.y_origin_order_id.name,
    #         'y_revision_count':self.y_origin_order_id.y_revision_count,
    #         'y_revision_order_ids':[(6, 0, self.y_origin_order_id.y_revision_order_ids.ids)]
    #     })
    #     old_origin.button_cancel()
    #     old_origin.unlink()
    #     return {
    #         'name': new_origin.name,
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'purchase.order',
    #         'res_id': new_origin.id
    #     }
    
 
    # def view_previous_versions(self):
    #     return {
    #         'name': 'Quotation',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'purchase.order',
    #         'domain': [('y_origin_order_id', '=', self.id)],
    #         'context': dict(self._context, create=False, edit=False)
    #     }
    
    # def action_create_invoice(self):
    #     for order in self:
    #         if order.y_origin_order_id:
    #             raise ValidationError(_("""Can not create a bill of a Revision"""))
    #     return super(PurchaseOrder, self).action_create_invoice()
    
    # def _send_reminder_mail(self, send_single=False):
    #     for order in self:
    #         if order.y_origin_order_id:
    #             raise ValidationError(_("""Can not send reminder mail of a Revision"""))
    #     return super(PurchaseOrder, self)._send_reminder_mail(send_single)
    
    def button_draft(self):
        raise ValidationError(_("""Invalid Action"""))




# class PortalMixin(models.AbstractModel):
#     _inherit = "portal.mixin"

    # @api.model
    # def action_share(self):
    #     if self.env.context['active_model'] == 'purchase.order':
    #         if self.env['purchase.order'].browse(self.env.context['active_id']).y_origin_order_id:
    #             raise ValidationError(_("""Can not Share a Revision"""))
    #     return super(PortalMixin, self).action_share()




class ResPartnerNew(models.Model):
    _inherit = "res.partner"


    y_purchase_doc_type_id = fields.Many2one('purchase.doc.type', string="Document Type")