# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
import itertools
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'


    y_partner_category = fields.Many2one('partner.category',string="Partner Category",domain="[('y_active_id', '=', True)]")
    y_customer = fields.Boolean(copy=False,string ="Customer")
    y_vendor = fields.Boolean(copy=False,string = "Vendor")
    y_contact = fields.Boolean('Contacts' ,compute='is_contact',store=True)
    y_partner = fields.Boolean('Partner')
    ref = fields.Char(tracking=True,copy=False)
    y_sequence_present = fields.Boolean(compute="check_seqnece_presence",store=True)
    y_is_partner_category_true = fields.Boolean(compute="check_partner_category_boolean", store=True)
    y_vendor_customer_is_true = fields.Boolean(store=True)
    
    
    
    
    @api.depends('y_partner_category')
    def check_partner_category_boolean(self):
        for rec in self:
            if rec.ref:
                rec.y_is_partner_category_true = True
            else:
                rec.y_is_partner_category_true = False
    
    @api.constrains('y_customer','y_vendor')
    def _check_partner_category(self):
        for record in self:
            if not record.y_partner_category:
                raise ValidationError("Please Select The Partner Category Before Approve")
    

    @api.depends('y_partner_category')
    def check_seqnece_presence(self):
        for rec in self:
            if rec.y_partner_category.y_partner_category:
                rec.y_sequence_present = True
            else:
                rec.y_sequence_present = False

    @api.onchange('y_customer')
    def onchange_customer(self):
        for each_sale in self:
            if each_sale.y_customer:
                each_sale.customer_rank = 1
 
    @api.onchange('y_vendor')
    def onchange_vendor(self):
        for each_sale in self:
            if each_sale.y_vendor:
                each_sale.supplier_rank = 1   

    @api.depends('y_customer','y_vendor')
    def is_contact(self):
        for each in self:
            if each.y_vendor or each.y_customer:
                each.y_contact= False
            else:
                each.y_contact = True
                
                
                
    # @api.model
    # def create(self, vals):
    #     if 'y_partner' in vals and vals['y_partner']:
    #         sequence_type =  vals.get('y_partner_category')
    #         sequence_type = self.env['partner.category'].browse(sequence_type)
    #         if sequence_type:
    #             vals['ref'] = sequence_type.y_partner_category.next_by_id()
    #     return super(ResPartner, self).create(vals)

    # def write(self, vals):
    #     if 'y_partner_category' in vals and vals['y_partner_category']:
    #         partner_category =  self.env['partner.category'].browse(vals.get('y_partner_category'))
    #         sequence_type = partner_category.y_partner_category
    #         if sequence_type:
    #             vals['ref'] = sequence_type.next_by_id()
    #     return super(ResPartner, self).write(vals)


    
    @api.onchange('y_partner_category')
    def onchange_partner(self):
        for l in self:
            if l.y_partner_category.y_partner_category:
                l.y_partner = True
            else:
                l.y_partner = False

    def approve_customer(self):
        self.message_post(body='Customer Approved')
        res = self.write({'y_customer':True})
        sequence_type = self.y_partner_category.y_partner_category
        if sequence_type and self.y_vendor_customer_is_true != True and not self.ref :
            self.ref = sequence_type.next_by_id()
            self.y_vendor_customer_is_true = True
        return res

    def approve_vendor(self):
        self.message_post(body='Vendor Approved')
        res = self.write({'y_vendor':True})
        sequence_type = self.y_partner_category.y_partner_category
        if sequence_type and self.y_vendor_customer_is_true != True and not self.ref:
            self.ref = sequence_type.next_by_id()
            self.y_vendor_customer_is_true = True
        return res
    
    @api.constrains('ref')
    def _check_duplicate_ref(self):
        moves = self.filtered(lambda move: move.ref and move.active != False)
        if not moves:
            return
        self.env["res.partner"].flush_model([
            'ref'
        ])
        # self.env["res.partner"].flush([
        #     "ref",
        # ])
        self._cr.execute('''
            SELECT move2.id
            FROM res_partner move
            INNER JOIN res_partner move2 ON
                move2.ref = move.ref AND move2.id != move.id
            WHERE move.id IN %s
        ''', [tuple(moves.ids)])
        duplicated_moves = self.browse([r[0] for r in self._cr.fetchall()])
        if duplicated_moves:
            raise ValidationError(_('Same Reference Is Already Exist')
            )
   

class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description ='Partner Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _parent_name = "y_zparent"
    _parent_store = True
    _rec_name = 'y_full_name'
    _order = 'y_full_name'

    y_name = fields.Char(string='Name',index=True,tracking=True)
    y_full_name = fields.Char(string='Category Name',store=True,compute='_compute_complete_name')
    y_zparent = fields.Many2one('partner.category',string='Parent',tracking=True)
    y_active_id = fields.Boolean(string='Release',tracking=True)
    y_partner_category = fields.Many2one('ir.sequence',string="Sequence",tracking=True)
    parent_path = fields.Char(index=True)
   
    @api.depends('y_name', 'y_zparent.y_name')
    def _compute_complete_name(self):
        for location in self:
            if location.y_zparent:
                location.y_full_name = '%s / %s' % (location.y_zparent.y_full_name, location.y_name)
            else:
                location.y_full_name = location.y_name

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    y_partner_category_id = fields.Many2one('partner.category',string="Partner Category",compute='get_partner_category',store=True)


    y_show_so_warning = fields.Boolean()
    @api.depends('partner_id')
    def get_partner_category(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.y_partner_category:
                    rec.y_partner_category_id =rec.partner_id.y_partner_category.id
                else:
                    rec.y_partner_category_id = False
            else:
                rec.y_partner_category_id = False


    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        if self.partner_id:
            if not self.partner_id.y_customer:
                raise AccessError('This customer is not approved. Kindly get the contact approved')
        return res



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('y_vendor', '=', True)]")
    y_partner_category_id = fields.Many2one('partner.category',string="Partner Category",compute='get_partner_category',store=True)

    @api.depends('partner_id')
    def get_partner_category(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.y_partner_category:
                    rec.y_partner_category_id =rec.partner_id.y_partner_category.id
                else:
                    rec.y_partner_category_id = False
            else:
                rec.y_partner_category_id = False


    def button_confirm(self):
        res = super(PurchaseOrder,self).button_confirm()
        if self.partner_id:
            if not self.partner_id.y_vendor:
                raise AccessError('This vendor is not approved. Kindly get the contact approved')
        return res

    def button_approve(self, force=False):        
        res = super(PurchaseOrder, self).button_approve(force=False)
        if self.partner_id:
            if not self.partner_id.y_vendor:
                raise AccessError('This vendor is not approved. Kindly get the contact approved')
        return res



class AccountInvoice(models.Model):
    _inherit = "account.move"

    y_is_customer = fields.Boolean('Customer',compute='change_domain',store=True)
    y_is_vendor = fields.Boolean('Vendor',compute='change_domain',store=True)
    partner_id = fields.Many2one(domain="['|',('y_customer', '=', y_is_customer),('y_vendor','=',y_is_vendor),('y_contact','=', False)]")
    y_partner_category_id = fields.Many2one('partner.category',string="Partner Category",compute='get_partner_category',store=True)

    @api.depends('partner_id')
    def get_partner_category(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.y_partner_category:
                    rec.y_partner_category_id =rec.partner_id.y_partner_category.id
                else:
                    rec.y_partner_category_id = False
            else:
                rec.y_partner_category_id = False


    @api.depends('partner_id')
    def change_domain(self):
        for rec in self:
            vendor_lit=['in_invoice','in_refund','in_receipt']
            customer_lit=['out_invoice','out_refund','out_receipt']
            if rec.move_type in vendor_lit:
                rec.y_is_vendor = True
            elif rec.move_type in customer_lit:
                rec.y_is_customer = True
            else:
                rec.y_is_vendor = False
                rec.y_is_customer = False

            

class account_payment(models.Model):
    _inherit = "account.payment"

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer/Vendor",
        store=True, readonly=False, ondelete='restrict',
        compute=False,
        domain="['|',('y_customer', '=', y_is_customer),('y_vendor','=',y_is_vendor),('y_contact','=', False)]",
        tracking=True,
        check_company=True)
    # partner_id = fields.Many2one('res.partner', string='Partner', tracking=True, readonly=True,states={'draft': [('readonly', False)]})
    y_is_customer = fields.Boolean('Customer')
    y_is_vendor = fields.Boolean('Vendor')

    @api.onchange('partner_type')
    def find_user(self):
        for rec in self:
            if rec.partner_type == 'customer':
                rec.y_is_customer = True
                rec.y_is_vendor = False
            elif rec.partner_type == 'supplier':
                rec.y_is_vendor = True
                rec.y_is_customer = False

class SaleReport(models.Model):
    _inherit = "sale.report"

    y_partner_category_id = fields.Many2one('partner.category',string="Partner Category",readonly=True)

    def _select(self):
        return super(SaleReport, self)._select() + ", s.y_partner_category_id as y_partner_category_id"
    
    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.y_partner_category_id"

class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    y_partner_category_id = fields.Many2one('partner.category',string="Partner Category",readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.y_partner_category_id as y_partner_category_id"
    
    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.y_partner_category_id"

class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    y_partner_category_id = fields.Many2one('partner.category',string="Partner Category",readonly=True)

    def _select(self):
        return super()._select() + ", move.y_partner_category_id as y_partner_category_id"

class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    action = fields.Selection(selection_add=[('create', 'Create a new customer/contact')])

class ContactRejectReason(models.TransientModel):
    _name = 'contact.reject.reason'
    _description = 'get reasons for not approved'


    @api.model
    def default_get(self, fields):
        result = super(ContactRejectReason, self).default_get(fields)
        active_id = self.env.context.get('y_active_id')
        cust_type = self.env.context.get('y_customer_type')        
        result['y_customer_type'] = cust_type
        record = self.env['res.partner'].sudo().browse(active_id)
        if record:
            result['y_partner_id'] = record.id            
        return result 

    y_customer_type = fields.Char()
    y_partner_id = fields.Many2one('res.partner')
    y_reasons = fields.Text('Reject Reason')

    def update_reason(self):
        if self.y_partner_id:
            if self.y_partner_id.y_customer == True:
                mesg =  """Reason For Rejection (%s) . """%(self.y_reasons)  
                self.y_partner_id.message_post(body=mesg)
                self.y_partner_id.write({'y_customer':False})
            if self.y_partner_id.y_vendor == True:
                mesg = """<p style="color:red;">%s</p>"""%(self.y_reasons)    
                self.y_partner_id.message_post(body=mesg)
                self.y_partner_id.write({'y_vendor':False})
            return True