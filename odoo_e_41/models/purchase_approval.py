# See LICENSE file for full copyright and licensing details.

from odoo import api, fields,models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date
from lxml import etree
import json
from odoo.tools import html2plaintext

def get_selection_label(self, object, field_name, field_value):
	return (dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])



class PurchaseDocType(models.Model):
    _inherit = 'purchase.doc.type'
    
    y_is_approval_required = fields.Boolean(default=True)
    y_currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, )

class PurchaseAppproval(models.Model):
    _name = "purchase.approval"
    _description ="purchase.approval"
    
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = "y_name"

    active = fields.Boolean(default=True)
    y_document_type_id = fields.Many2one("purchase.doc.type","Document Type",tracking=True)
    y_name = fields.Char("Name")
    y_warehouse_id = fields.Many2one("stock.warehouse","Warehouse",tracking=True)
    y_approval_lines = fields.One2many("purchase.approval.line","y_purchase_approval_id",string="Approval Lines",tracking=True)
    y_lvl_amt_approval_lines = fields.One2many("purchase.lvlamt.approval","y_lvl_approval_id",string="Lvl Amt Approval Lines",tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True)
    y_currency_id = fields.Many2one('res.currency', string='Currency', tracking=True,related='y_document_type_id.y_currency_id')

    y_approval_method = fields.Selection(selection=[
            ('stages', 'Levels'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount')
            ],string='Approval Method',default='amount',tracking=True)
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)

    @api.constrains('y_name','company_id')
    def check_purchase_approval_name(self):
        for rec in self:
            docs=rec.env['purchase.approval'].search([('y_name','=',rec.y_name),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""name already exists!"""))

    @api.onchange('y_document_type_id')
    def _update_name(self):
        if self.y_document_type_id:
            self.y_name = self.y_document_type_id.y_name

    @api.constrains('y_document_type_id', 'y_warehouse_id')
    def _check_duplicate(self):
        existing_id=self.env['purchase.approval'].search([
                                            ('y_document_type_id','=',self.y_document_type_id.id),
                                            ("y_warehouse_id",'=',self.y_warehouse_id.id),
                                            ])
        if not len(existing_id) ==1:
            raise UserError (_("You Can't create the Purchase Approval from the same Warehouse and Document Type"))


class PurchaseAppprovalLine(models.Model):
    _name = "purchase.approval.line"
    _description ="purchase.approval.line"

    def _group_internal_users(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []


    y_user_ids = fields.Many2many("res.users",string="Users",domain=_group_internal_users)
    y_purchase_approval_id = fields.Many2one("purchase.approval",string="Appove")
    y_approval_amount = fields.Float("Amount(Up To)")
    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")


    y_approval_one= fields.Boolean("1")
    y_approval_two= fields.Boolean("2")
    y_approval_three= fields.Boolean("3")
    y_approval_four = fields.Boolean("4")
    y_approval_five = fields.Boolean("5")
    y_approval_all= fields.Boolean("Parallel")
    y_role = fields.Char("Role")


    @api.onchange('y_approval_all')
    def _update_approval_all(self):
        if self.y_approval_all:
            self.y_approval_one = False
            self.y_approval_two = False
            self.y_approval_three = False
            self.y_approval_four = False
            self.y_approval_five = False



    @api.onchange('y_approval_one')
    def _update_y_approval_one(self):
        if self.y_approval_one:
            self.y_approval_two = False
            self.y_approval_three = False
            self.y_approval_four = False
            self.y_approval_five = False
            self.y_approval_all = False

    @api.onchange('y_approval_two')
    def _update_y_approval_two(self):
        if self.y_approval_two:
            self.y_approval_one = False
            self.y_approval_three = False
            self.y_approval_four = False
            self.y_approval_five = False
            self.y_approval_all = False

    @api.onchange('y_approval_three')
    def _update_y_approval_three(self):
        if self.y_approval_three:
            self.y_approval_one = False
            self.y_approval_two = False
            self.y_approval_four = False
            self.y_approval_five = False
            self.y_approval_all = False

    @api.onchange('y_approval_four')
    def _update_y_approval_four(self):
        if self.y_approval_four:
            self.y_approval_one = False
            self.y_approval_two = False
            self.y_approval_three = False
            self.y_approval_five = False
            self.y_approval_all = False

    @api.onchange('y_approval_five')
    def _update_y_approval_five(self):
        if self.y_approval_five:
            self.y_approval_one = False
            self.y_approval_two = False
            self.y_approval_three = False
            self.y_approval_four = False
            self.y_approval_all = False


    

    @api.constrains('y_approval_amount_from')
    def approval_amount_number(self):
        total_approval = self.y_purchase_approval_id.y_approval_lines.mapped('id')
        purchase_approval_line_obj = self.env['purchase.approval.line'].browse(total_approval[-2:-1])
        for rec in self:
             if rec.y_approval_amount_from < purchase_approval_line_obj.y_approval_amount_to:
                 raise UserError(_("Amount(From) should be greater than previous record Amount(To)"))
             if rec.y_approval_amount_to < rec.y_approval_amount_from:
                 raise UserError(_("Amount(To) is less than Amount(From)"))

    @api.constrains('y_approval_amount_from','y_approval_amount_to')
    def approval_amount_number(self):
        total_approval = self.y_purchase_approval_id.y_approval_lines.mapped('id')
        purchase_approval_line_obj = self.env['purchase.approval.line'].browse(total_approval[-2:-1])
        for rec in self:

            if rec.y_approval_amount_from < purchase_approval_line_obj.y_approval_amount_to:
                raise UserError(_("Amount(From) should be greater than previous record Amount(To)"))
            if rec.y_approval_amount_to < rec.y_approval_amount_from:
                raise UserError(_("Amount(To) is less than Amount(From)"))

class PurchaseOrderApprovalLvlAmt(models.Model):
    _name="purchase.order.approval.lvlsamt"
    _description  = 'purchase.order.approval Lvl Amt'

    y_approval_level = fields.Selection(selection=[
            ('1stlvlapproval', '1 Level Approval'),
            ('2ndlvlapproval', '2 Level Approval'),
            ('3rdlvlapproval', '3 Level Approval'),
            ('4thlvlapproval', '4 Level Approval'),
            ('5thlvlapproval', '5 Level Approval'),


            ],string='Approval Level',copy=False)
    y_lvl1_user_ids = fields.Many2many("res.users",'lvl4_user',string="Level 1 User")
    y_lvl2_user_ids = fields.Many2many("res.users",'lvl5_user',string="Level 2 User")
    y_lvl3_user_ids = fields.Many2many("res.users",'lvl6_user',string="Level 3 User")
    y_lvl4_user_ids = fields.Many2many("res.users",'lvl9_user',string="Level 4 User")
    y_lvl5_user_ids = fields.Many2many("res.users",'lvl10_user',string="Level 5 User")


    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")
    y_purchase_lvl_id = fields.Many2one('purchase.order')
    y_is_approval_completed = fields.Boolean(default=False)
    y_is_1st_user_completed = fields.Boolean(string="1st user completed")
    y_is_2nd_user_completed = fields.Boolean(string="2nd user completed")
    y_is_3rd_user_completed = fields.Boolean(string="3rd user completed")
    y_is_4th_user_completed = fields.Boolean(string="4th user completed")
    y_is_5th_user_completed = fields.Boolean(string="5th user completed")

    y_approved_date1 = fields.Datetime("Approved Date 1")
    y_remarks = fields.Char(string="Remarks")

    y_approved_date2 = fields.Datetime("Approved Date 2")

    y_approved_date3 = fields.Datetime("Approved Date 3")
    y_approved_date4 = fields.Datetime("Approved Date 4")
    y_approved_date5 = fields.Datetime("Approved Date 5")
    
    
    

class PurchaseOrderApproval(models.Model):
    _name="purchase.order.approval"
    _description  = 'purchase.order.approval'

    y_approvals = fields.Selection(selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', 'All'),
            ('amount', 'Amount'),
            ],string='Approvals')
    y_is_approve = fields.Boolean("Approved")
    order_id = fields.Many2one('purchase.order')
    y_user_ids= fields.Many2many('res.users', string='Users')
    y_amount = fields.Float("Amount")
    y_approved_date = fields.Datetime("Approved Date")
    y_remarks = fields.Char("Remarks")
    y_role = fields.Char("Role")
    y_approval_method = fields.Selection(selection=[
            ('stages', 'Levels'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount'),
            ],string='Approval Method')
    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")
    y_is_email_sent = fields.Boolean(string="Is Email Sent")



    
class PurchaseLevelAmmountApproval(models.Model):
    _name = "purchase.lvlamt.approval"
    _description = "Purchase Lvl&Amt Approval"

    def _group_internal_users(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    y_approval_level = fields.Selection(selection=[
            ('1stlvlapproval', '1 Level Approval'),
            ('2ndlvlapproval', '2 Level Approval'),
            ('3rdlvlapproval', '3 Level Approval'),
            ('4thlvlapproval', '4 Level Approval'),
            ('5thlvlapproval', '5 Level Approval'),

            ],string='Approval Level',copy=False)
    y_lvl1_user_ids = fields.Many2many("res.users",'lvl1_user',string="Level 1 User",domain=_group_internal_users)
    y_lvl2_user_ids = fields.Many2many("res.users",'lvl2_user',string="Level 2 User",domain=_group_internal_users)
    y_lvl3_user_ids = fields.Many2many("res.users",'lvl3_user',string="Level 3 User",domain=_group_internal_users)
    y_lvl4_user_ids = fields.Many2many("res.users",'lvl7_user',string="Level 4 User",domain=_group_internal_users)
    y_lvl5_user_ids = fields.Many2many("res.users",'lvl8_user',string="Level 5 User",domain=_group_internal_users)

    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")
    y_lvl_approval_id = fields.Many2one('purchase.approval',string="Lvl and Approval")

    @api.constrains('y_approval_amount_from', 'y_approval_amount_to')
    def approval_lvl_amount_number(self):
        for rec in self:
            approval_lines = rec.y_lvl_approval_id.y_lvl_amt_approval_lines.sorted('id')
            if not approval_lines:
                raise UserError(_("Approval lines cannot be empty."))
            previous_to_amount = 0.0
            for index, line in enumerate(approval_lines):
                if index == 0:
                    if line.y_approval_amount_from != 0.0:
                        raise UserError(_("The first approval line must start from Amount From 0.0."))
                else:
                    if line.y_approval_amount_from != previous_to_amount + 1:
                        raise UserError(_("Amount From ({}) should be equal to the previous record Amount To ({}) plus one."
                                          .format(line.y_approval_amount_from, previous_to_amount)))
                if line.y_approval_amount_to <= line.y_approval_amount_from:
                    raise UserError(_("Amount To ({}) should be greater than Amount From ({})"
                                      .format(line.y_approval_amount_to, line.y_approval_amount_from)))
                previous_to_amount = line.y_approval_amount_to
            if rec.y_approval_amount_to <= rec.y_approval_amount_from:
                raise UserError(_("Amount To ({}) should be greater than Amount From ({})"
                                  .format(rec.y_approval_amount_to, rec.y_approval_amount_from)))
                
    

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order','mail.thread', 'mail.activity.mixin']

    # y_incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    y_approved_by = fields.Many2one('res.users' , string='Approved By')
    y_approve_doc = fields.Boolean('Approve Doc',copy=False)
    y_doc_type_id = fields.Many2one(tracking=True,)
    y_show_po_warning = fields.Char(string="Warning",compute='_compute_is_show_budget_warning_move',default=False,store=True)
    y_exchange_rate = fields.Float(string="Currency Rate",compute='_compute_exchange_rate',default=False,store=True,help="This rate will be used to convert the PO value and check the approval range in comapny currency.")
    
    
    def update_old_records_exchange_rate(self):
        for rec in self:
            dec_type = rec.y_doc_type_id
            rec.write({'y_doc_type_id': False})
            
            rec.write({'y_doc_type_id': dec_type.id,})
            rec.y_approver_visible = False
    

    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        fields_triggering_compute = ['picking_type_id', 'y_doc_type_id', 'currency_id', 'amount_total', 'order_line']

        if any(field in vals for field in fields_triggering_compute):
            self.with_context(bypass_write=True).get_data()

        return result


   
    
    @api.depends('y_doc_type_id')
    def _compute_exchange_rate(self):
        for rec in self:
            create_date_str = ''
            if rec.currency_id and rec.company_id.currency_id:
                if rec.currency_id.id != rec.company_id.currency_id.id:
                    if rec.create_date:
                        create_date_str = rec.create_date.strftime('%Y-%m-%d')
                    rate_found = False
                    for rate in rec.currency_id.rate_ids:
                        rate_date_str = rate.name.strftime('%Y-%m-%d')
                        if create_date_str == rate_date_str:
                            rec.y_exchange_rate = 1 / rate.company_rate
                            rate_found = True
                            break  
                    if not rate_found:
                        rec.y_exchange_rate = 1 / rec.currency_id.rate_ids[0].company_rate
                else:
                    rec.y_exchange_rate = 1
            else:
                rec.y_exchange_rate = 1
                
    @api.depends('order_line.price_unit', 'y_doc_type_id')
    def _compute_is_show_budget_warning_move(self):
        for rec in self:
            if rec.order_line:
                if rec.y_doc_type_id:
                    last_line = self.env['purchase.approval'].search([
                    ('y_document_type_id', '=', rec.y_doc_type_id.id)
                    ], limit=1)
                    if last_line and last_line.y_lvl_amt_approval_lines:
                        last_approval_amount = last_line.y_lvl_amt_approval_lines[-1].y_approval_amount_to
                        first_approval_amount = last_line.y_lvl_amt_approval_lines[0].y_approval_amount_from
                    else:
                        last_approval_amount = 0.0
                    if rec.amount_total > last_approval_amount and rec.currency_id == rec.company_id.currency_id:
                        message = f"The PO total amount '{rec.amount_total}' exceeds the approved limit '{last_approval_amount}'"
                        rec.y_show_po_warning = message
                    elif first_approval_amount > rec.amount_total and rec.currency_id == rec.company_id.currency_id:
                        message = f"The PO total amount '{rec.amount_total}' less then approved limit '{first_approval_amount}'"
                        rec.y_show_po_warning = message
                    elif (rec.amount_total * rec.y_exchange_rate) > last_approval_amount and rec.currency_id != rec.company_id.currency_id :
                        exchange_rate = rec.amount_total * rec.y_exchange_rate   
                        message = f"The PO total amount '{exchange_rate}'('{rec.currency_id.symbol}{rec.amount_total}') exceeds the approved limit '{last_approval_amount}'"
                        rec.y_show_po_warning = message
                    elif first_approval_amount > (rec.amount_total * rec.y_exchange_rate) and rec.currency_id != rec.company_id.currency_id:
                        exchange_rate = rec.amount_total * rec.y_exchange_rate 
                        message = f"The PO total amount '{exchange_rate}({rec.currency_id.symbol}{rec.amount_total}') less then approved limit '{first_approval_amount}'"
                        rec.y_show_po_warning = message
                    else:
                        rec.y_show_po_warning = False
                else:
                    rec.y_show_po_warning = False


    
    y_po_approval_method = fields.Selection(selection=[
            ('stages', 'Level'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount'),
            ],string='Approval Method')


    y_purchase_approval_line = fields.One2many("purchase.order.approval",'order_id',copy=False)
    y_purchase_lvl_amt_approval_line = fields.One2many("purchase.order.approval.lvlsamt",'y_purchase_lvl_id',copy=False)


    y_approval_data = fields.Boolean("Data",copy=False,store=True)
    y_current_approvall = fields.Integer("Current Approval",default=1,copy=False)
    y_approval_method = fields.Char("Check Approval Method",copy=False)
    y_is_approved = fields.Boolean(string="Is Approved",copy=False,default=False)
    y_is_rejected = fields.Boolean(string="Is Rejected",copy=False)
    state = fields.Selection(selection_add=[
            ('reject', 'Rejected')
        ])
    #  ondelete={'reject': 'cascade'}

    y_to_approve_states = fields.Selection(selection=[
            
            ('to_approve_state1', '1st Approval Pending'),
            ('to_approve_state2', '2nd Approval Pending'),
            ('to_approve_state3', '3rd Approval Pending'),
            ('to_approve_state4', '4th Approval Pending'),
            ('to_approve_state5', '5th Approval Pending'),

            ('approved', 'Approved'),
            ('na','N/A'),
            ('not_applicable_for_approval','NAA'),
            ('reject','Rejected')
            ],string='To Approve State',default='na',store=True,copy=False)


    y_to_approve_states_bool = fields.Boolean(string="Is states Bool")

    y_is_approval_req = fields.Boolean(string="Is Approval Request",store=True)

    y_is_1st_lvl_approval = fields.Boolean(string="Is 1st Lvl Approval")
    y_is_2nd_lvl_approval = fields.Boolean(string="Is 2nd Lvl Approval")
    y_is_3rd_lvl_approval = fields.Boolean(string="Is 3rd Lvl Approval")
    y_is_4th_lvl_approval = fields.Boolean(string="Is 4th Lvl Approval")
    y_is_5th_lvl_approval = fields.Boolean(string="Is 5th Lvl Approval")

    y_show_warning = fields.Boolean(string="Show Warning")
    y_product_ids = fields.Many2many('product.product', string="Products")

    # is_approval_req = fields.Boolean(compute='onchange_compute_POL_approval_req', store=True)
    y_approver_visible = fields.Boolean(string="Approver Visible",copy=False)
    
   
    
    
    def post_approval_message(self):
        for rec in self.y_purchase_lvl_amt_approval_line:
            if rec.y_approval_level in ['1stlvlapproval', '2ndlvlapproval', '3rdlvlapproval', '4thlvlapproval', '5thlvlapproval']:
                level = rec.y_approval_level.split('lvl')[0]
                msg = f"Request Sent To {level} Level Approval"
                
                # Post the message to the record (optional)
                self.message_post(body=msg)
                email_template = self.env.ref('odoo_e_41.email_template_signup_approve').id
                if email_template:
                    email_template_obj = self.env['mail.template'].browse(email_template)
                    for user_id in self.y_purchase_lvl_amt_approval_line.y_lvl1_user_ids:
                        # print(user_id,"ppppppppsssssssssssssssssssssssssss")
                        user = user_id
                        # print(user,"ffffffffffffffffffffffffffffffffff")
                        email_values = {
                            'email_to': user.login,
                            'email_from': self.user_id.login,
                            }
                        # print(email_values,"ppppppppppppppppppppppppppppppppppppppppppppppppppp")
                        email_template_obj.send_mail(self.id, email_values = email_values)

                        # Create mail activity only for users in y_lvl1_user_ids
                        if user_id:
                            type_id = self.env['mail.activity.type'].search([('name', '=', 'Purchase Email')], limit=1)
                            res_model = self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')], limit=1)
                            subject = _('Purchase Order Pending Approval')
                            body = f'"{user.name}" Requested an approval "{self.name}"'
                            
                            vals = {
                                'res_model_id': res_model.id,
                                'res_model': res_model.model,
                                'res_id': self.id,
                                'activity_type_id': type_id.id,
                                'user_id': user.id,
                                'date_deadline': date.today(),
                                'summary': subject,
                                'note': html2plaintext(body),
                            }
                            activity = self.env['mail.activity'].create(vals)

    def request_for_approve(self):
        for rec in self:
            rec.y_approver_visible = True
            rec.state = 'to approve'
            rec.y_to_approve_states = 'to_approve_state1'
            rec.post_approval_message()
            rec.order_line.with_context(validate_analytic=True)._validate_analytic_distribution()

    def get_set_draft(self):
        if self.state == 'reject':
            self.state = 'draft'
            self.y_approver_visible = False
            self.y_doc_type_id = False
            approval_obj = self.env['purchase.order.approval.lvlsamt'].search([('y_purchase_lvl_id', '=', self.id)]).unlink()
            approval_order_obj = self.env['purchase.order.approval'].search([('order_id', '=', self.id)]).unlink()
            self.y_current_approvall = 1
            
    @api.onchange('currency_id')
    def onchange_currency_purchase(self):
        for rec in self:
            rec.y_doc_type_id = False

    @api.onchange('y_doc_type_id')
    def get_doc_product(self):
        if self.y_doc_type_id:
            product_obj = self.env['product.product'].search([])
            product_list = []
            for product in product_obj:
                if self.y_doc_type_id in product.product_tmpl_id.y_doc_type_ids:
                    product_list.append(product.id)
            self.y_product_ids = product_list
            
   


    def button_draft(self):
        res = super().button_draft()
        self.y_purchase_approval_line.unlink()
        self.y_purchase_lvl_amt_approval_line.unlink()
        self._compute_lines_approved()
        self.get_data()


    @api.model
    def get_view(self, view_id=None, view_type=None, **options):
        result = super().get_view(view_id, view_type, **options)
        if view_type == 'form':
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//field"):
                modifiers = json.loads(node.get("modifiers", '{}'))
                if type(modifiers.get('readonly')) == list:
                    modifiers['readonly'] = ['|'] + modifiers['readonly'] + [('state', '=', 'reject')]
                elif not type(modifiers.get('readonly')) == bool:
                    modifiers['readonly']=[['state', '=', 'reject']]
                    node.set("modifiers", json.dumps(modifiers))
            result['arch'] = etree.tostring(doc)
        return result

    # @api.model
    # def get_view(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(PurchaseOrder, self).get_view(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu,)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//field"):
    #             modifiers = json.loads(node.get("modifiers"))
    #             if type(modifiers.get('readonly')) == list:
    #                 modifiers['readonly'] = ['|'] + modifiers['readonly'] + [('state', '=', 'reject')]
    #             elif not type(modifiers.get('readonly')) == bool:
    #                 modifiers['readonly']=[['state', '=', 'reject']]
    #                 node.set("modifiers", json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc)
    #     return res


    # @api.depends('picking_type_id','y_doc_type_id','currency_id','amount_total')
    def get_data(self):
        for each in self:
            # each.y_approver_visible = True
            each.y_approval_data = False
            each.y_purchase_approval_line.unlink()
            each.y_purchase_lvl_amt_approval_line.unlink()
            if each.picking_type_id.id and each.y_approval_data == False:
                approval_ids = self.env['purchase.approval'].search([('y_document_type_id','=',each.y_doc_type_id.id)])
                if approval_ids.y_approval_method in ('stages','amount'):
                    if self.y_purchase_approval_line:
                            all_approvals = [x.y_is_approve for x in self.y_purchase_approval_line]
                            if True in all_approvals:
                                raise UserError (_("You cannot change the document type once approved, Kindly Discard the PO and create a new PO"))
                            else:
                                self.y_purchase_approval_line = False

                    for each_line in approval_ids.y_approval_lines:
                        if approval_ids.y_approval_method == 'stages':
                            if each_line.y_approval_one:
                                value='1'
                            elif each_line.y_approval_two:
                                value='2'
                            elif each_line.y_approval_three:
                                value='3'
                            elif each_line.y_approval_four:
                                value='4'
                            elif each_line.y_approval_five:
                                value='5'
                            else:
                                value='6'
                        else:
                            value = 'amount'

                        valas={
                        'y_approvals':value ,
                        'y_user_ids': [(6, 0, each_line.y_user_ids.ids)],
                        'y_amount':each_line.y_approval_amount,
                        'y_approval_amount_from':each_line.y_approval_amount_from,
                        'y_approval_amount_to':each_line.y_approval_amount_to,
                        'y_role':each_line.y_role,
                        'order_id':each.id,
                        'y_approval_method':each_line.y_purchase_approval_id.y_approval_method,
                        }
                        self.env['purchase.order.approval'].create(valas)
                        each.y_approval_method = approval_ids.y_approval_method
                else:
                    for each_line in approval_ids.y_lvl_amt_approval_lines:
                        val_from = []
                        val_to = []
                        for rec in approval_ids.y_lvl_amt_approval_lines:
                            val_from.append(rec.y_approval_amount_from)
                            val_to.append(rec.y_approval_amount_to)
                        if self.currency_id == self.company_id.currency_id:
                            if val_from[0] < self.amount_total or self.amount_total > val_to[-1]:
                                if each_line.filtered(lambda line : int(line.y_approval_amount_from) <= each.amount_total and int(line.y_approval_amount_to) >= each.amount_total):
                                    val = each_line.filtered(lambda line : int(line.y_approval_amount_from) <= each.amount_total and int(line.y_approval_amount_to) >= each.amount_total)
                                    # print(each_line.filtered(lambda line : int(line.y_approval_amount_from) <= each.amount_total and int(line.y_approval_amount_to) >= each.amount_total))
                                    # print("Im from IF________________________________________________________________________________")
                                    # print("\n"*25)
                                    valas={
                                    'y_approval_level':val.y_approval_level,
                                    'y_lvl1_user_ids': [(6, 0, val.y_lvl1_user_ids.ids)],
                                    'y_lvl2_user_ids': [(6, 0, val.y_lvl2_user_ids.ids)],

                                    'y_lvl3_user_ids': [(6, 0, val.y_lvl3_user_ids.ids)],
                                    'y_lvl4_user_ids': [(6, 0, val.y_lvl4_user_ids.ids)],
                                    'y_lvl5_user_ids': [(6, 0, val.y_lvl5_user_ids.ids)],

                                    'y_approval_amount_from':val.y_approval_amount_from,
                                    'y_approval_amount_to':val.y_approval_amount_to,
                                    'y_purchase_lvl_id':each.id,
                                    }
                                    line = self.env['purchase.order.approval.lvlsamt'].create(valas)
                                    print("DSDSDSDSDSDSDSDSDGHJKL;",line.y_approval_level)
                                    self.y_is_approval_req = False
                                    
                        elif self.currency_id != self.company_id.currency_id:
                            amount_total = self.amount_total * self.y_exchange_rate
                            if val_from[0] < amount_total or amount_total > val_to[-1]:
                                if each_line.filtered(lambda line : int(line.y_approval_amount_from) <= amount_total and int(line.y_approval_amount_to) >= amount_total):
                                    val = each_line.filtered(lambda line : int(line.y_approval_amount_from) <= amount_total and int(line.y_approval_amount_to) >= amount_total)
                                    
                                    valas={
                                    'y_approval_level':val.y_approval_level,
                                    'y_lvl1_user_ids': [(6, 0, val.y_lvl1_user_ids.ids)],
                                    'y_lvl2_user_ids': [(6, 0, val.y_lvl2_user_ids.ids)],

                                    'y_lvl3_user_ids': [(6, 0, val.y_lvl3_user_ids.ids)],
                                    'y_lvl4_user_ids': [(6, 0, val.y_lvl4_user_ids.ids)],
                                    'y_lvl5_user_ids': [(6, 0, val.y_lvl5_user_ids.ids)],

                                    'y_approval_amount_from':val.y_approval_amount_from,
                                    'y_approval_amount_to':val.y_approval_amount_to,
                                    'y_purchase_lvl_id':each.id,
                                    }
                                    line = self.env['purchase.order.approval.lvlsamt'].create(valas)
                                    print("DSDSDSDSDSDSDSDSDGHJKL;",line.y_approval_level)
                                    self.y_is_approval_req = False
                                    
                                

                            

                                
                        else:
                            # print(each_line.filtered(lambda line : int(line.y_approval_amount_from) <= each.amount_total and int(line.y_approval_amount_to) >= each.amount_total))
                            # print("Im from ELSE________________________________________________________________________________")
                            # print("\n"*25)
                            valas={
                            'y_approval_level':each_line.y_approval_level,
                            'y_lvl1_user_ids': [(6, 0, each_line.y_lvl1_user_ids.ids)],
                            'y_lvl2_user_ids': [(6, 0, each_line.y_lvl2_user_ids.ids)],

                            'y_lvl3_user_ids': [(6, 0, each_line.y_lvl3_user_ids.ids)],
                            'y_lvl4_user_ids': [(6, 0, each_line.y_lvl4_user_ids.ids)],
                            'y_lvl5_user_ids': [(6, 0, each_line.y_lvl5_user_ids.ids)],

                            'y_approval_amount_from':each_line.y_approval_amount_from,
                            'y_approval_amount_to':each_line.y_approval_amount_to,
                            'y_purchase_lvl_id':each.id,
                            }
                            self.env['purchase.order.approval.lvlsamt'].create(valas)   
                            self.y_is_approval_req = True                         
                        
                
                    each.y_is_1st_lvl_approval = any(line.y_lvl1_user_ids for line in each.y_purchase_lvl_amt_approval_line)
                    each.y_is_2nd_lvl_approval = any(line.y_lvl2_user_ids for line in each.y_purchase_lvl_amt_approval_line)
                    each.y_is_3rd_lvl_approval = any(line.y_lvl3_user_ids for line in each.y_purchase_lvl_amt_approval_line)
                    each.y_is_4th_lvl_approval = any(line.y_lvl4_user_ids for line in each.y_purchase_lvl_amt_approval_line)
                    each.y_is_5th_lvl_approval = any(line.y_lvl5_user_ids for line in each.y_purchase_lvl_amt_approval_line)

            each.y_approval_data = True
            each.with_context(bypass_write=True).write({'y_approval_data': True})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    @api.model
    def create(self, vals):
        record = super(PurchaseOrder, self).create(vals)
        record.get_data()
        return record

    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        fields_triggering_compute = ['picking_type_id', 'y_doc_type_id', 'currency_id', 'amount_total', 'order_line']

        if any(field in vals for field in fields_triggering_compute):
            self.with_context(bypass_write=True).get_data()

        return result

    @api.onchange('y_doc_type_id')
    def _compute_lines_approved(self):
        if  self.y_doc_type_id.y_is_approval_required == True:
            self.y_is_approved = True
            approvalls = self.env['purchase.doc.type'].search([('id','=',self.y_doc_type_id.id)])
            if not approvalls:
                raise ValidationError("""Approvals Not Configured""")
            approval_ids = self.env['purchase.approval'].search([('y_document_type_id','=',self.y_doc_type_id.id)])
            if not approval_ids:
                raise ValidationError("""Approvals Not Configured""")
            self.y_po_approval_method = approval_ids.y_approval_method
            self.y_to_approve_states = 'to_approve_state1'
        else:
            self.y_is_approved = False
        if self.y_doc_type_id.y_is_approval_required == False:
            
            self.y_to_approve_states = 'na'
        if self.y_doc_type_id.y_is_approval_required == True and self.y_approver_visible == False:
            print("APPROVER VISIBLE FALSE")
            self.y_to_approve_states = 'not_applicable_for_approval'
        
        

    def button_approve(self):
        for rec in self:
            rec.order_line.with_context(validate_analytic=True)._validate_analytic_distribution()
            if not rec.y_doc_type_id:
                raise ValidationError(_("""Mapping Document type is required to confirm a Purchase Quotation"""))
            rec.y_quotation_number = rec.name
            rec.date_approve = date.today()
            rec.name = rec.y_doc_type_id.y_sequence_id.next_by_id()
        return super(PurchaseOrder, self).button_approve()

        
    def button_confirm(self):
        self.ensure_one()
        val_from = []
        val_to = []
        if self.y_purchase_lvl_amt_approval_line != False:
            for rec in self.y_purchase_lvl_amt_approval_line:
                val_from.append(rec.y_approval_amount_from)
                val_to.append(rec.y_approval_amount_to)
        if self.y_purchase_approval_line and self.y_doc_type_id.y_is_approval_required == True:
            if self.y_approval_method == 'amount':
                all_approvals = [x.y_is_approve for x in self.y_purchase_approval_line]
                if any(all_approvals) or self.y_purchase_approval_line.filtered(lambda line : int(line.y_approval_amount_from) >= self.amount_total):
                    return self.button_approve()
                else:
                    raise UserError (_("Purchase Approval Pending"))
            elif self.y_approval_method == 'stages':
                all_approvals = [x.y_is_approve for x in self.y_purchase_approval_line]
                if False in all_approvals:
                    raise UserError (_("Purchase Approval Pending"))
                else:
                    return self.button_approve()
        elif self.y_purchase_lvl_amt_approval_line and self.y_doc_type_id.y_is_approval_required == True:

            approval_ids = self.env['purchase.approval'].search([('y_document_type_id','=',self.y_doc_type_id.id)])

            if approval_ids.y_approval_method == 'lvlsamt':
                if self.amount_total < val_from[0] or self.amount_total > val_to[-1]:
                    return self.button_approve()
                else:
                    all_approvals = [x.y_is_approval_completed for x in self.y_purchase_lvl_amt_approval_line]
                    if False in all_approvals:
                        raise UserError (_("Purchase Approval Pending"))
                    else:
                        return self.button_approve()

        else:
            # if self.y_doc_type_id:
            raise UserError (_("Purchase Approval Pending"))
            # else:
            #     return super(PurchaseOrder, self).button_confirm()


    def get_approval(self):
        current_user_id = self.env.uid
        self.y_approved_by = current_user_id
        user = self.env['res.users'].browse(current_user_id)

        
        approval_ids = self.env['purchase.approval'].search([('y_document_type_id','=',self.y_doc_type_id.id)])

        if approval_ids.y_approval_method in ('stages','amount'):
            for rec in approval_ids:
                if rec:
                    curr_method = rec.y_approval_method
                    all_approvals = [x.y_approvals for x in self.y_purchase_approval_line]
                    if curr_method == 'stages':
                        current_appoval_line = self.y_purchase_approval_line.filtered(lambda line : int(line.y_approvals) == self.y_current_approvall)
                        if current_appoval_line:
                            if self.env.user.id in current_appoval_line.y_user_ids.ids :
                                current_appoval_line.y_is_approve = True
                                current_appoval_line.y_approved_date = datetime.now()
                                self.y_current_approvall +=1
                                self.y_approve_doc = True

                                
                                msg = """
                                        <div> The purchase order has been approved by: %s</div>
                                        """%(user.name)
                                self.message_post(body=msg)
                                
                                for user_id in self.current_appoval_line.y_user_ids.ids:
                                    user = self.env['res.users'].browse(user_id)
                                   
                                    if user_id:
                                        type_id =self.env['mail.activity.type'].search([('name','=','Purchase Email')])
                                        res_model = self.env['ir.model'].sudo().search([('model','=','purchase.order')])
                                        subject = 'Request For Approval'
                                        body = f'"{user.name}" Requested an approval "{self.name}"'
                                        vals={
                                            'res_model_id':res_model.id,
                                            'res_model':res_model.name,
                                            'res_id':self.id,
                                            'activity_type_id':type_id.id,
                                            'user_id':user.id,
                                            'date_deadline':date.today(),
                                            'summary': subject,
                                            'note': html2plaintext(body)
                                        }
                                        activity = self.env['mail.activity'].create(vals)
                                
                            else:
                                raise UserError (_(" You can't approve the order"))
                    
                    elif curr_method == 'amount':
                        if self.y_purchase_approval_line.filtered(lambda line : int(line.y_approval_amount_from) <= self.amount_total):
                            new_ids = self.y_purchase_approval_line.filtered(lambda line : int(line.y_approval_amount_from) <= self.amount_total and int(line.y_approval_amount_to) >= self.amount_total)
                            user_list =[]
                            for each in new_ids:
                                if self.env.user.id in each.y_user_ids.ids:
                                    user_list.append(each)
                            if user_list:
                                user_list[0].y_is_approve = True
                                self.y_approve_doc = True
                                user_list[0].y_approved_date = datetime.now()
                                self.button_confirm()
                            else:
                                raise UserError (_("You can't approve the order"))
                        else:
                            self.button_confirm()
                else:
                    raise UserError (_(" Create the purchase approval "))
            for rec in self.y_purchase_approval_line:
                if rec.y_is_approve==False and rec.y_approvals=='1':
                    self.y_to_approve_states = 'to_approve_state2'
                    break

                if rec.y_is_approve==False and rec.y_approvals=='2' :
                    self.y_to_approve_states = 'to_approve_state2'
                    break

                if rec.y_is_approve==False and rec.y_approvals=='3' :
                    self.y_to_approve_states = 'to_approve_state3'
                    break
                if rec.y_is_approve==False and rec.y_approvals=='4' :
                    self.y_to_approve_states = 'to_approve_state4'
                    break
                if rec.y_is_approve==False and rec.y_approvals=='5' :
                    self.y_to_approve_states = 'to_approve_state5'
                    break


                data = self.y_purchase_approval_line.mapped('y_is_approve')
                print(data,'data')
                if all(data) == True:
                    self.y_to_approve_states = 'approved'
                    self.button_confirm()
                    break
                # [('y_is_approval_completed','=',True),('y_is_1st_user_completed','=',True)]
        else:
            current_user = self.env.user
            for y_lvl_approval_lines in self.y_purchase_lvl_amt_approval_line:
                print(y_lvl_approval_lines.y_lvl1_user_ids.ids,y_lvl_approval_lines.y_lvl2_user_ids.ids,y_lvl_approval_lines.y_lvl3_user_ids.ids,y_lvl_approval_lines.y_lvl4_user_ids.ids)
                if self.env.user.id in y_lvl_approval_lines.y_lvl1_user_ids.ids:
                    if not y_lvl_approval_lines.y_is_1st_user_completed:
                        y_lvl_approval_lines.y_is_1st_user_completed = True
                        y_lvl_approval_lines.y_approved_date1 = datetime.now()
                        self.y_approve_doc = True
                        self.y_to_approve_states = 'to_approve_state2'
                        first_approval_msg = f"First Approval Is Done: {current_user.name}"
                        self.message_post(body=first_approval_msg)
                        # msg = " Second Approval Is Pending By: {}".format(', '.join(y_lvl_approval_lines.y_lvl2_user_ids.mapped('name')))
                        # message_post = self.message_post(body=msg)  
                        
                        email_template = self.env.ref('odoo_e_41.email_template_signup_approve').id
                        if email_template:
                            email_template_obj = self.env['mail.template'].browse(email_template)
                            for user_id in self.y_purchase_lvl_amt_approval_line.y_lvl2_user_ids.ids:
                                user = self.env['res.users'].browse(user_id)
                                email_values = {
                                    'email_to': user.login,
                                    'email_from': self.env.user.email,
                                    }
                                email_template_obj.send_mail(self.id, email_values = email_values)
                                if user_id:
                                    type_id =self.env['mail.activity.type'].search([('name','=','Purchase Email')])
                                    res_model = self.env['ir.model'].sudo().search([('model','=','purchase.order')])
                                    subject = 'Request For Approval'
                                    body = f'"{user.name}" Requested an approval "{self.name}"'
                                    vals={
                                        'res_model_id':res_model.id,
                                        'res_model':res_model.name,
                                        'res_id':self.id,
                                        'activity_type_id':type_id.id,
                                        'user_id':user.id,
                                        'date_deadline':date.today(),
                                        'summary': subject,
                                        'note': html2plaintext(body)
                                    }
                                    activity = self.env['mail.activity'].create(vals)

                        if y_lvl_approval_lines.y_approval_level in ('2ndlvlapproval','3rdlvlapproval','4rdlvlapproval','5rdlvlapproval'):       
                           pending_state = get_selection_label(self,'purchase.order','y_to_approve_states',self.y_to_approve_states)
                           msg = " Second Approval Is Pending By: {}".format(', '.join(y_lvl_approval_lines.y_lvl2_user_ids.mapped('name')))
                           message_post = self.message_post(body=msg)   

                    else:
                        raise UserError(_("You can't approve the order"))
                
                if self.env.user.id in y_lvl_approval_lines.y_lvl2_user_ids.ids:
                    if y_lvl_approval_lines.y_is_1st_user_completed:

                        if not y_lvl_approval_lines.y_is_2nd_user_completed:
                            y_lvl_approval_lines.y_is_2nd_user_completed = True
                            y_lvl_approval_lines.y_approved_date2 = datetime.now()
                            self.y_approve_doc = True
                            self.y_to_approve_states = 'to_approve_state3'
                            second_approval_msg = f"Second Approval Is Done: {current_user.name}"
                            self.message_post(body=second_approval_msg)
                            
                            email_template = self.env.ref('odoo_e_41.email_template_signup_approve').id
                            if email_template:
                                email_template_obj = self.env['mail.template'].browse(email_template)
                                for user_id in self.y_purchase_lvl_amt_approval_line.y_lvl3_user_ids.ids:
                                    user = self.env['res.users'].browse(user_id)
                                    email_values = {
                                        'email_to': user.login,
                                        'email_from': self.env.user.email,
                                        }
                                    email_template_obj.send_mail(self.id, email_values = email_values)
                                    if user_id:
                                        type_id =self.env['mail.activity.type'].search([('name','=','Purchase Email')])
                                        res_model = self.env['ir.model'].sudo().search([('model','=','purchase.order')])
                                        subject = 'Request For Approval'
                                        body = f'"{user.name}" Requested an approval "{self.name}"'
                                        vals={
                                            'res_model_id':res_model.id,
                                            'res_model':res_model.name,
                                            'res_id':self.id,
                                            'activity_type_id':type_id.id,
                                            'user_id':user.id,
                                            'date_deadline':date.today(),
                                            'summary': subject,
                                            'note': html2plaintext(body)
                                        }
                                        activity = self.env['mail.activity'].create(vals)
                            if y_lvl_approval_lines.y_approval_level in ('3rdlvlapproval','4rdlvlapproval','5rdlvlapproval'):       
                                pending_state = get_selection_label(self,'purchase.order','y_to_approve_states',self.y_to_approve_states)
                                msg = "Third Approval Is Pending By: {}".format(', '.join(y_lvl_approval_lines.y_lvl3_user_ids.mapped('name')))
                                message_post = self.message_post(body=msg)

                            
                        else:
                            raise UserError(_("You can't approve the order"))
                        
                    else:
                            raise UserError(_("You can't approve the order"))

                if self.env.user.id in y_lvl_approval_lines.y_lvl3_user_ids.ids:
                    if y_lvl_approval_lines.y_is_2nd_user_completed:
                        if not y_lvl_approval_lines.y_is_3rd_user_completed:
                            y_lvl_approval_lines.y_is_3rd_user_completed = True
                            y_lvl_approval_lines.y_approved_date3 = datetime.now()
                            self.y_approve_doc = True
                            self.y_to_approve_states = 'to_approve_state4'
                            third_approval_msg = f"Third Approval Is Done: {current_user.name}"
                            self.message_post(body=third_approval_msg)
                            
                            email_template = self.env.ref('odoo_e_41.email_template_signup_approve').id
                            if email_template:
                                email_template_obj = self.env['mail.template'].browse(email_template)
                                for user_id in self.y_purchase_lvl_amt_approval_line.y_lvl4_user_ids.ids:
                                    user = self.env['res.users'].browse(user_id)
                                    email_values = {
                                        'email_to': user.login,
                                        'email_from': self.env.user.email,
                                        }
                                    email_template_obj.send_mail(self.id, email_values = email_values)
                                    if user_id:
                                        type_id =self.env['mail.activity.type'].search([('name','=','Purchase Email')])
                                        res_model = self.env['ir.model'].sudo().search([('model','=','purchase.order')])
                                        subject = 'Request For Approval'
                                        body = f'"{user.name}" Requested an approval "{self.name}"'
                                        vals={
                                            'res_model_id':res_model.id,
                                            'res_model':res_model.name,
                                            'res_id':self.id,
                                            'activity_type_id':type_id.id,
                                            'user_id':user.id,
                                            'date_deadline':date.today(),
                                            'summary': subject,
                                            'note': html2plaintext(body)
                                        }
                                        activity = self.env['mail.activity'].create(vals)
                            if y_lvl_approval_lines.y_lvl4_user_ids:       
                                pending_state = get_selection_label(self,'purchase.order','y_to_approve_states',self.y_to_approve_states)
                                msg = "fourth Approval Is Pending By: {}".format(', '.join(y_lvl_approval_lines.y_lvl4_user_ids.mapped('name')))
                                message_post = self.message_post(body=msg)

                        else:
                            raise UserError(_("You can't approve the order"))
                        
                    else:
                        raise UserError(_("You can't approve the order"))
                    

                if self.env.user.id in y_lvl_approval_lines.y_lvl4_user_ids.ids:
                    if y_lvl_approval_lines.y_is_3rd_user_completed:
                        if  not y_lvl_approval_lines.y_is_4th_user_completed:
                            y_lvl_approval_lines.y_is_4th_user_completed = True
                            y_lvl_approval_lines.y_approved_date4 = datetime.now()
                            self.y_approve_doc = True
                            self.y_to_approve_states = 'to_approve_state5'
                            fourth_approval_msg = f"Fourth Approval Is Done: {current_user.name}"
                            self.message_post(body=fourth_approval_msg)
                            
                            email_template = self.env.ref('odoo_e_41.email_template_signup_approve').id
                            if email_template:
                                email_template_obj = self.env['mail.template'].browse(email_template)
                                for user_id in self.y_purchase_lvl_amt_approval_line.y_lvl5_user_ids.ids:
                                    user = self.env['res.users'].browse(user_id)
                                    email_values = {
                                        'email_to': user.login,
                                        'email_from': self.env.user.email,
                                        }
                                    email_template_obj.send_mail(self.id, email_values = email_values)
                                    if user_id:
                                        type_id =self.env['mail.activity.type'].search([('name','=','Purchase Email')])
                                        res_model = self.env['ir.model'].sudo().search([('model','=','purchase.order')])
                                        subject = 'Request For Approval'
                                        body = f'"{user.name}" Requested an approval "{self.name}"'
                                        vals={
                                            'res_model_id':res_model.id,
                                            'res_model':res_model.name,
                                            'res_id':self.id,
                                            'activity_type_id':type_id.id,
                                            'user_id':user.id,
                                            'date_deadline':date.today(),
                                            'summary': subject,
                                            'note': html2plaintext(body)
                                        }
                                        activity = self.env['mail.activity'].create(vals)
                            if y_lvl_approval_lines.y_lvl4_user_ids:       
                                pending_state = get_selection_label(self,'purchase.order','y_to_approve_states',self.y_to_approve_states)
                                msg = "Fifth Approval Is Pending By: {}".format(', '.join(y_lvl_approval_lines.y_lvl4_user_ids.mapped('name')))
                                message_post = self.message_post(body=msg)
                        else:
                            raise UserError(_("You can't approve the order"))
                        

                    else:
                        raise UserError(_("You can't approve the order"))

                if self.env.user.id in y_lvl_approval_lines.y_lvl5_user_ids.ids:
                    if y_lvl_approval_lines.y_is_4th_user_completed:
                        if  not y_lvl_approval_lines.y_is_5th_user_completed:
                            y_lvl_approval_lines.y_is_5th_user_completed = True
                            y_lvl_approval_lines.y_approved_date5 = datetime.now()
                            self.y_approve_doc = True
                            fifth_approval_msg = f"Fifth Approval Is Done: {current_user.name}"
                            self.message_post(body=fifth_approval_msg)
                            
                            
                        else:
                            raise UserError(_("You can't approve the order"))
                    else:
                            raise UserError(_("You can't approve the order"))


            for rec in self.y_purchase_lvl_amt_approval_line:
                if rec.y_approval_level == '1stlvlapproval':
                    if rec.y_is_1st_user_completed==True:
                        rec.y_is_approval_completed = True
                        self.y_approve_doc = True

                        self.button_confirm()
                       


                if rec.y_approval_level == '2ndlvlapproval':
                    if rec.y_is_1st_user_completed==True and  rec.y_is_2nd_user_completed==True:
                        rec.y_is_approval_completed = True

                        self.button_confirm()
                       
                if rec.y_approval_level == '3rdlvlapproval':
                    if rec.y_is_1st_user_completed==True and  rec.y_is_2nd_user_completed==True and rec.y_is_3rd_user_completed==True:
                        rec.y_is_approval_completed = True
                        self.button_confirm()
                        

                if rec.y_approval_level == '4thlvlapproval':

                    if rec.y_is_1st_user_completed==True and  rec.y_is_2nd_user_completed==True and rec.y_is_3rd_user_completed==True and rec.y_is_4th_user_completed==True:
                        rec.y_is_approval_completed = True
                        self.button_confirm()
                        

                if rec.y_approval_level == '5thlvlapproval':
                    if rec.y_is_1st_user_completed==True and  rec.y_is_2nd_user_completed==True and rec.y_is_3rd_user_completed==True and rec.y_is_4th_user_completed==True and rec.y_is_5th_user_completed==True:
                        rec.y_is_approval_completed = True
                        self.button_confirm()


            # for rec in self.y_purchase_lvl_amt_approval_line:
            #     if rec.y_approval_level == '2ndlvlapproval':
            #         if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==False:
            #             self.y_approve_doc = True


            #     if rec.approval_level == '3rdlvlapproval':
            #         if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==False and rec.y_is_3rd_user_completed==False:
            #             self.y_to_approve_states = 'to_approve_state2'
                   

            #         if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==True and rec.y_is_3rd_user_completed==False:
            #             self.to_approve_states = 'to_approve_state3'

            #     if rec.approval_level == '4thlvlapproval':
            #         if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==False and rec.is_3rd_user_completed==False and rec.y_is_4th_user_completed==False:
            #             self.to_approve_states = 'to_approve_state3'
                    

            #         if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==True and rec.is_3rd_user_completed==False and rec.y_is_4th_user_completed==False:
            #             self.to_approve_states = 'to_approve_state4'

            #     if rec.approval_level == '5thlvlapproval':
            #         if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==False and rec.is_3rd_user_completed==False and rec.y_is_4th_user_completed==False and rec.y_is_5th_user_completed==False:
            #             self.to_approve_states = 'to_approve_state4'
                    

            #         if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==True and rec.is_3rd_user_completed==False and rec.y_is_4th_user_completed==False and rec.y_is_5th_user_completed==False:
            #             self.to_approve_states = 'to_approve_state5'





    def button_unlock(self):
        res = super(PurchaseOrder, self).button_unlock()
        if not self.env.user.has_group('odoo_e_41.acess_po_unlock'):
            raise ValidationError(_("""You do not have access to unlock the Purchase Order"""))
        return res

                

class onchangefuncforPOl(models.Model):
    _inherit = 'purchase.order.line'

    # 
#     @api.onchange('price_unit')
#     def newonchange_POL_is_approval_req(self):
        # self.env['purchase.order'].get_data()
        # print("Im from Before Onchange_________________________________________________________","\n"*25)
        # self.order_id.get_data()
        # self.order_id.request_for_approve()
        # print("Im from After Onchange_________________________________________________________","\n"*25)
