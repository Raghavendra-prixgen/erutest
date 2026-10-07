from odoo import models,tools, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class RejectResons(models.TransientModel):
    _name = "reject.reason"

    y_reject_reason = fields.Char('Reject Reason')

    def pass_y_reject_reason(self):
        advance_payment_obj = self.env['purchase.account.payment'].browse(self._context.get('active_id'))
        advance_payment_obj.y_reject_reason = self.y_reject_reason



class PaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    y_advance_request_required = fields.Boolean(string="Down Payment Request")


    @api.constrains('y_advance_request_required')
    def check_advance_request_required(self):
        for rec in self:
            value = rec.payment_id.line_ids.filtered(lambda x: x.y_advance_request_required != False)
            if len(value) > 1:
                raise UserError(_("Create Only one down payment request term"))


class AdvanceRequestApprovalForm(models.Model):
    _name = "advance.request.approval.form"
    _description = "Down Payment Request Approval Form"


    y_advance_sequence_id = fields.Many2one('ir.sequence',string="Sequence No.")
    y_company_id = fields.Many2one('res.company', 'Company')
    y_approval_user_ids = fields.Many2many('res.users',string="Approval User")
    active = fields.Boolean(default=True)

    @api.model
    def create(self,vals):
        advance_request_approval_form_obj = self.env['advance.request.approval.form'].search(['|', ('y_company_id', '=', False), ('y_company_id', '=',vals.get('y_company_id'))])
        if len(advance_request_approval_form_obj)>0:
            raise UserError(_("Cannot Create Multiple Config Records"))
         
        return super().create(vals)


class PurchaseAccountDown(models.Model):
    _name = "purchase.account.down"
    _description = 'Purchases & Account Union'

   
    y_partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
    y_currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    y_company_id = fields.Many2one('res.company', 'Company', readonly=True)
    y_payment_id = fields.Many2one('account.payment', string='Boe Template', readonly=True)
    y_purchase_account_payment_id = fields.Many2one('purchase.account.payment', string='Purchase Order', readonly=True)

    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, 'purchase_account_down')
    #     self.env.cr.execute("""
    #         CREATE OR REPLACE VIEW purchase_account_down AS (
    #             SELECT
    #                 id,y_partner_id,  y_currency_id,
    #                 id as y_payment_id, NULL as y_purchase_account_payment_id
    #             FROM account_payment
                  
    #         UNION
    #             SELECT
    #                 id,y_partner_id,y_currency_id,
    #                 NULL as y_payment_id, id as y_purchase_account_payment_id
    #             FROM purchase_account_payment
               
    #         )""")






class PurchaseAccount(models.Model):
    _name = "purchase.account.payment"
    _description = "Purchase Account Payment"
    _rec_name = "y_sequence"

    y_remark = fields.Text('Remark')
    y_sequence = fields.Char(string="Request No.")
    y_partner_id = fields.Many2one('res.partner',string="Vendor")
    y_company_id = fields.Many2one('res.company', 'Company', readonly=True)
    y_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency')
    y_amount = fields.Monetary(currency_field='y_currency_id',string="Amount")
    y_date = fields.Date(string="Date")
    y_ref = fields.Char(string="Memo")
    y_reject_reason = fields.Char(string="Reject Reason")
    y_purchase_id = fields.Many2one('purchase.order',string="Purchase")
    y_approved_by = fields.Many2one('res.users',string="Approved/Rejected By")
    y_is_advance_payment_done = fields.Boolean(string="Is Advance Payment Done")
    y_payment_status = fields.Selection([('draft', 'Not Paid'),('confirm', 'Paid'),], default="draft", string="Payment Status")
    y_approval_status = fields.Selection([('approval_pending', 'Approval Pending'),('approved', 'Approved'),('rejected', 'Reject')], default="approval_pending", string="Approval Status")
    y_invoice_date_due = fields.Datetime(string='Effective Date')



    def name_get(self):
        result = None 
        for rec in self:
            if rec.y_purchase_id:
                result = '%s-%s' % (rec.y_purchase_id.name, rec.y_sequence)
            else:
                result = '%s' % (rec.y_sequence)
        return result
    
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name_get()
    

    



    def action_approve(self):
        if self.env.user in self.y_purchase_id.y_advance_request_form_approval_id.mapped('y_approval_user_ids'):
            self.y_approved_by = self.env.user.id

            self.write({'y_approval_status':'approved'})
        else:
            raise UserError (_("Oops!!!! You can't approve the request"))



    def action_reject(self):
        if self.env.user in self.y_purchase_id.y_advance_request_form_approval_id.mapped('y_approval_user_ids'):
            self.y_approved_by = self.env.user.id

            self.write({'y_approval_status':'rejected'})
            return {

                        'name': 'Warning',

                        'type': 'ir.actions.act_window',

                        'res_model': 'reject.reason',

                        'view_mode': 'form',

                        'view_type': 'form',

                        'target': 'new'

                          }
        else:
            raise UserError (_("Oops!!!! You can't reject the request"))



class PurchaseAdvancePaymentWizard(models.TransientModel):
    _name = "advance.payment.wizard"
    _description = " "

    def get_po_currency(self):
        return self.env['purchase.order'].browse(self._context.get('y_purchase_id')).currency_id.id

    def get_amount_percentage(self):
        purchase_obj = self.env['purchase.order'].browse(self._context.get('y_purchase_id'))
        if purchase_obj.payment_term_id:
            term_line_ids = purchase_obj.payment_term_id.line_ids.filtered(lambda x:x.y_advance_request_required == True)
            if term_line_ids:
                if term_line_ids.value == 'percent':
                    return 'percentage'
                elif term_line_ids.value == 'fixed':
                    return 'amount'

    y_name = fields.Char('Name')
    # journal_id = fields.Many2one('account.journal', store=True, readonly=False,domain="[ ('type', 'in', ('bank', 'cash'))]")
    y_payment_amount = fields.Float('Payment Amount')
    y_payment_status = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'),], default="draft", string="Payment Status")
    y_remark = fields.Text('Remark')
    y_amount_or_percentage = fields.Selection([('amount','Amount'),('percentage','Percentage')],default=get_amount_percentage,string=" ")
    y_percentage = fields.Float(string="Percentage")
    y_company_id = fields.Many2one('res.company', 'Company', readonly=True)
    y_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',default=get_po_currency)

    y_invoice_date_due = fields.Datetime(string='Effective Date')
 

    @api.onchange('y_amount_or_percentage')
    def onchange_amount_percemtage(self):
        purchase_obj = self.env['purchase.order'].browse(self.env.context.get('y_purchase_id'))
        if purchase_obj.payment_term_id:
            if self.y_amount_or_percentage == 'amount':
                self.y_payment_amount = purchase_obj.payment_term_id.line_ids.filtered(lambda x:x.y_advance_request_required == True and x.value == 'fixed').value_amount
            else:
                self.y_percentage = purchase_obj.payment_term_id.line_ids.filtered(lambda x:x.y_advance_request_required == True and x.value == 'percent').value_amount


    def calculate_percent(self,y_percentage,value):
        percentage_value = y_percentage/100
        return (percentage_value*value)

    @api.onchange('y_percentage')
    def calculate_amount(self):
        for rec in self:
            purchase_obj = self.env['purchase.order'].browse(self.env.context.get('y_purchase_id'))
            if rec.y_percentage:
                rec.y_payment_amount = rec.calculate_percent(rec.y_percentage,purchase_obj.amount_total)

    
    @api.onchange('y_payment_amount')
    def field_validation(self):
        if self.y_payment_amount:
            purchase_obj = self.env['purchase.order'].browse(self.env.context.get('y_purchase_id'))
            if self.y_payment_amount <= 0:
                return {'warning': {
                'title': _('Invalid Amount'),
                'message': _('Please Enter The Valid Amount!')
                }}

            elif not (self.y_payment_amount + sum([payment.amount for payment in purchase_obj.y_purchase_account_payment_ids if payment.y_is_advance_payment_done == False and payment.y_approval_status == 'approved']) <= purchase_obj.amount_total):
                return {'warning': {
                'title': _('Invalid Amount'),
                'message': _('Amount Exceeded to Payable Purchase Amount!')
                }}

    @api.constrains('y_payment_amount')
    def _check_value(self):
        if self.y_payment_amount <= 0.0:
            raise ValidationError("Please Enter The Valid Amount!")


    def create_advance_payment(self):
        if self.env.context.get('y_purchase_id'):
            purchase_obj = self.env['purchase.order'].browse(self.env.context.get('y_purchase_id'))
            print( purchase_obj.y_advance_request_form_approval_id.y_advance_sequence_id.next_by_id()," purchase_obj.y_advance_request_form_approval_id.y_advance_sequence_id.next_by_id().............")
            print(purchase_obj,"purchase_obj........")
            if (self.y_payment_amount + sum([payment.amount for payment in purchase_obj.y_purchase_account_payment_ids if payment.y_is_advance_payment_done == False and payment.y_approval_status == 'approved']) <= purchase_obj.amount_total):
                payment_dict = {
                                'y_partner_id': purchase_obj.partner_id.id,
                                'y_amount': self.y_payment_amount, 
                                'y_currency_id': self.y_currency_id.id, 
                                'y_date': datetime.now(), 
                                'y_ref': 'Adv :'+ ' ' + purchase_obj.name, 
                                'y_purchase_id':purchase_obj.id,
                                'y_remark':self.y_remark,
                                'y_invoice_date_due':self.y_invoice_date_due,
                                'y_sequence': purchase_obj.y_advance_request_form_approval_id.y_advance_sequence_id.next_by_id() or 'New'}
                payment_obj = self.env['purchase.account.payment'].create(payment_dict)
            else:
                return {'warning': {
                'title': _('Invalid Amount'),
                'message': _('Amount Exceeded to Payable Purchase Amount!')}}

    # def create_advance_payment(self):
    #     if self.env.context.get('y_purchase_id'):
    #         purchase_obj = self.env['purchase.order'].browse(self.env.context.get('y_purchase_id'))
    #         if (self.payment_amount + sum([payment.amount for payment in purchase_obj.payment_ids if payment.state == 'posted']) <= purchase_obj.amount_total):
    #             payment_dict = {'name':False,
    #                             'payment_type':'outbound',
    #                             'partner_type': 'supplier',
    #                             'partner_id': purchase_obj.partner_id.id,
    #                             'destination_account_id': purchase_obj.partner_id.property_account_receivable_id.id,
    #                             'is_internal_transfer': False,
    #                             'journal_id': self.journal_id.id,
    #                             'edi_document_ids': [],
    #                             'payment_token_id': False, 
    #                             'partner_bank_id': False, 
    #                             'amount': self.payment_amount, 
    #                             'currency_id': purchase_obj.currency_id.id, 
    #                             'date': datetime.now(), 
    #                             'ref': 'Adv :'+ ' ' +purchase_obj.name, 
    #                             'message_follower_ids': [], 
    #                             'activity_ids': [], 
    #                             'message_ids': [],
    #                             'remark':self.remark,}
    #             payment_obj = self.env['account.payment'].create(payment_dict)
    #             payment_obj.purchase_id = purchase_obj.id
    #             payment_obj.partner_type = 'supplier'
    #             purchase_obj.message_chatter()
    #             payment_obj.message_chatter(self.remark, purchase_obj)
    #         else:
    #             return {'warning': {
    #             'title': _('Invalid Amount'),
    #             'message': _('Amount Exceeded to Payable Purchase Amount!')}}


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    def _get_default_journal(self):
  
        return self.env['account.move']._search_default_journal(('bank', 'cash'))

    y_purchase_id = fields.Many2one('purchase.order','Purchase Order')
    y_remark = fields.Text('Remark')
    y_purchase_account_down_id = fields.Many2one('purchase.account.down',string="Purchase Order")
    y_purchase_account_payment_id = fields.Many2one('purchase.account.payment',
        string='Down Payment Request')
    y_payment_id = fields.Many2one('account.payment')

    @api.onchange('partner_id')
    def _onchange_partner_purchase_account_payment(self):
        for payment in self:
            if payment.y_purchase_account_payment_id and payment.y_purchase_account_payment_id.y_partner_id != payment.partner_id:
                raise ValidationError("Vendor Miss Match")


    def action_post(self):
        res = super().action_post()
        for rec in self:
            if rec.y_purchase_account_payment_id and rec.y_purchase_account_payment_id.y_partner_id != rec.partner_id:
                raise ValidationError("Vendor Miss Match")

            if rec.y_purchase_account_payment_id:
                rec.y_purchase_account_payment_id.y_is_advance_payment_done = True

                rec.y_purchase_account_payment_id.y_payment_status = 'confirm'
                rec.y_purchase_account_payment_id.y_purchase_id.y_is_payment_completed = True
                rec.y_purchase_id = rec.y_purchase_account_payment_id.y_purchase_id.id
        return res

   


    @api.onchange('y_purchase_account_down_id', 'y_purchase_account_payment_id')
    def _onchange_sale_auto_complete(self):
        y_purchase_account_payment_id = self.y_purchase_account_down_id.y_purchase_account_payment_id or self.y_purchase_account_payment_id
        if y_purchase_account_payment_id :
            journal_id = self.y_purchase_account_down_id.y_purchase_account_payment_id.journal_id or self.y_purchase_account_payment_id.journal_id
            if journal_id:
                self.journal_id = journal_id
        return super()._onchange_sale_auto_complete()

    @api.onchange('y_purchase_account_down_id','y_purchase_account_payment_id')
    def _onchange_sale_auto_complete(self):
        if self.y_purchase_account_down_id.y_payment_id:
            self.payment_id = self.y_purchase_account_down_id.y_payment_id._origin
        elif self.y_purchase_account_down_id.y_purchase_account_payment_id:
            self.y_purchase_account_down_id = self.y_purchase_account_down_id.y_purchase_account_payment_id
        self.y_purchase_account_down_id = False

        if not self.y_purchase_account_payment_id:
            return

        self.partner_id = self.y_purchase_account_payment_id.y_partner_id.id
        self.payment_type = 'outbound'
        self.partner_type = 'supplier'
        # self.journal_id = self.journal_id.id
        self.payment_method_line_id = self.payment_method_line_id.id

        self.amount = self.y_purchase_account_payment_id.y_amount
        self.ref = self.y_purchase_account_payment_id.y_ref
        self.is_internal_transfer = False
        # self.journal_id = self.y_purchase_account_payment_id.journal_id.id
    
    # @api.onchange('journal_id')
    # def _onchange_journal_id(self):
    #     if self.y_purchase_account_payment_id:
    #         if self.journal_id.currency_id != self.y_purchase_account_payment_id.y_currency_id:
    #             raise ValidationError("Currency id mismatch")   


    # @api.depends('journal_id','y_purchase_account_payment_id')
    # def _compute_currency_id(self):
        
    #     super(AccountPaymentInherit,self)._compute_currency_id()
    #     if self.y_purchase_account_payment_id:
    #         self.currency_id = self.y_purchase_account_payment_id.currency_id.id




    def message_chatter(self, y_remark, purchase_obj):
        display_msg = ""
        if y_remark:
            display_msg += """<b>Remark: </b>  """ + y_remark +"""."""
        self.message_post(body=display_msg)

    def unlink(self):
        for each in self:
            if each.y_purchase_id:
                raise UserError(_("Can not delete Purchase Order Advance Payments"))
        return super(AccountPaymentInherit, self).unlink()


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    y_purchase_account_payment_ids = fields.One2many('purchase.account.payment','y_purchase_id')
    y_is_payment_completed = fields.Boolean(copy=False,string="Payment Completed")
    y_advance_request_form_approval_id = fields.Many2one('advance.request.approval.form',string="Advance Request Approval")
    y_advace_request_count = fields.Integer(compute="get_count_advace_request_count",string="Advance Request Count")

    

    @api.depends('y_purchase_account_payment_ids')
    def get_count_advace_request_count(self):
        for order in self:
            order.y_advace_request_count = len(order.y_purchase_account_payment_ids)

    def purchase_account_payment_view(self):

        return  {"name":"Down Payment Request",
                "type": "ir.actions.act_window",
                "res_model": "purchase.account.payment",
                "view_mode":'tree',
                "context":dict(y_purchase_id=self.id,create=False,edit=False),
                "domain":[('y_purchase_id','=',self.id)],

                }

    # Down Payment Request
   
    def create_down_payment(self,object):
        advance_request_form_approval_obj = self.env['advance.request.approval.form'].search([],limit=1)
        
        # if  object.invoice_status in 'to invoice':
        #     raise UserError(_("Waiting bills, down payment request cannot be raised !"))
        
        if object.invoice_status in 'invoiced':
            raise UserError(_("Fully billed, down payment request cannot be raised !"))
        
        elif object.state not in ['purchase','done']:
            
            raise UserError(_('Down Payment Request can be processed only if the Order is in Purchase Order State!'))

        elif not  advance_request_form_approval_obj:
            raise UserError(_("Please Map Approvals for Down Payment Request"))

        
        else:
            object.y_advance_request_form_approval_id = advance_request_form_approval_obj.id
            
            return  {
                "name":"Down Payment Request",
                "type": "ir.actions.act_window",
                "res_model": "advance.payment.wizard",
                "views": [[False, "form"]],
                "target": 'new',
                "context":{'y_purchase_id':object.id},
                }


    def action_view_advance_payment(self):
        return {
                "name":"Payments",
                "type": "ir.actions.act_window",
                "res_model": "account.payment",
                "views": [[False, "tree"], [False, "form"]],
                'view_id': self.env.ref('odoo_e_27_b.account_payment_temp_id').id,
                "domain": [["purchase_id", "=", self.id]],
                }

    def message_chatter(self):
        display_msg = """<br>Down Payment Requested By <b>""" + str(self.partner_id.name) + """</b> at """ + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + """."""
        self.message_post(body=display_msg)
        
    def button_cancel(self):
        res = super(PurchaseOrderInherit, self).button_cancel()
        for rec in self:
            if any(rec.y_purchase_account_payment_ids.filtered(lambda x:x.y_approval_status == 'approved')):
                raise UserError("Unable to Cancel the Purchase Order, as Down Payment Request is raised against this Purchase Order")
            
        return res
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
