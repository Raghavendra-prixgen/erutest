# See LICENSE file for full copyright and licensing details.

from odoo import api, fields,models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date
from lxml import etree
import simplejson 
import json
from odoo.tools import html2plaintext


def get_selection_label(self, object, field_name, field_value):
	return (dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

class CustomSaleDocType(models.Model):
    _inherit= 'sale.doc.type'

    y_is_approval_required = fields.Boolean(default=True) #comment,,,,,,,,,,


class SaleAppproval(models.Model):
    _name = "sale.approval"
    _description ="sale.approval"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = 'y_name'

    active = fields.Boolean(default=True)
    y_document_type_id = fields.Many2one("sale.doc.type","Document Type",tracking=True)
    y_name = fields.Char("Name")
    y_warehouse_id = fields.Many2one("stock.warehouse","Warehouse",tracking=True)
    y_approval_lines = fields.One2many("sale.approval.line","y_sale_approval_id",tracking=True)
    y_lvl_amt_approval_lines = fields.One2many("sale.lvlamt.approval","y_lvl_approval_id",tracking=True)

    y_approval_method = fields.Selection(selection=[
            
            ('stages', 'Levels'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount')
            ],string='Approval Method',default='amount',tracking=True)
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)

    @api.constrains('y_name','y_company_id')
    def check_sale_approval_name(self):
        for rec in self:
            docs=rec.env['sale.approval'].search([('y_name','=',rec.y_name),('y_company_id','=',rec.y_company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""name already exists!"""))

    @api.onchange('y_document_type_id')
    def _update_name(self):
        if self.y_document_type_id:
            self.y_name = self.y_document_type_id.y_name





    @api.constrains('y_document_type_id', 'y_warehouse_id')
    def _check_duplicate(self):
        existing_id=self.env['sale.approval'].search([
                                            ('y_document_type_id','=',self.y_document_type_id.id),
                                            ("y_warehouse_id",'=',self.y_warehouse_id.id),
                                            ])
        if not len(existing_id) ==1:
            raise UserError (_("You Can't create the sale Approval from the same Warehouse and Document Type"))


class SaleAppprovalLine(models.Model):
    _name = "sale.approval.line"
    _description ="sale.approval.line"

    def _group_internal_users(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []


    y_user_ids = fields.Many2many("res.users",string="Users",domain=_group_internal_users)
    y_sale_approval_id = fields.Many2one("sale.approval",string="Appove")
    y_approval_amount = fields.Float("Amount(UP To)")
    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")


    y_approval_one= fields.Boolean("1")
    y_approval_two= fields.Boolean("2")
    y_approval_three= fields.Boolean("3")
    y_approval_all= fields.Boolean("Parallel")
    y_role = fields.Char("Role")


    @api.onchange('y_approval_all')
    def _update_approval_all(self):
        if self.y_approval_all:
            self.y_approval_one = False
            self.y_approval_two = False
            self.y_approval_three = False
    @api.onchange('y_approval_one')
    def _update_approval_one(self):
        if self.y_approval_one:
            self.y_approval_two = False
            self.y_approval_three = False
            self.y_approval_all = False

    @api.onchange('y_approval_two')
    def _update_approval_two(self):
        if self.y_approval_two:
            self.y_approval_one = False
            self.y_approval_three = False
            self.y_approval_all = False

    @api.onchange('y_approval_three')
    def _update_approval_three(self):
        if self.y_approval_three:
            self.y_approval_one = False
            self.y_approval_two = False
            self.y_approval_all = False
    
        
    @api.constrains('y_approval_amount_from','y_approval_amount_to')
    def approval_amount_number(self):
        if self.y_sale_approval_id.y_approval_method in ('amount'):


        
            filterd_ids = self.y_sale_approval_id.y_approval_lines
            for record in filterd_ids:
                if record != filterd_ids[0]:
                    filterd_line_ids = filterd_ids.mapped('id')
                    approval_line_id = record.env['sale.approval.line'].browse(filterd_line_ids[filterd_line_ids.index(record.id)-1])
                    if record.y_approval_amount_from <= approval_line_id.y_approval_amount_to:
                        raise UserError(_("Amount From({}) should be greater than previous record Amount To({})".format(record.y_approval_amount_from,approval_line_id.y_approval_amount_to)))
    
            for rec in self:
                if rec.y_approval_amount_to <= rec.y_approval_amount_from:
                    raise UserError(_("Amount To ({}) is less than Amount From ({})".format(rec.y_approval_amount_to,rec.y_approval_amount_from)))

                


class SalesOrderApprovalLvlAmt(models.Model):
    _name="sale.order.approval.lvlsamt"
    _description  = 'sale.order.approval Lvl Amt'

    y_approval_level = fields.Selection(selection=[
            ('1stlvlapproval', '1 Level Approval'),
            ('2ndlvlapproval', '2 Level Approval'),
            ('3rdlvlapproval', '3 Level Approval'),
            ],string='Approval Level',copy=False)
    y_lvl1_user_ids = fields.Many2many("res.users",'lvl44_user',string="Level 1 User")
    y_lvl2_user_ids = fields.Many2many("res.users",'lvl55_user',string="Level 2 User")
    y_lvl3_user_ids = fields.Many2many("res.users",'lvl66_user',string="Level 3 User")
    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")
    y_sale_lvl_id = fields.Many2one('sale.order')
    y_is_approval_completed = fields.Boolean(default=False)
    y_is_1st_user_completed = fields.Boolean(string="1st user completed")
    y_is_2nd_user_completed = fields.Boolean(string="2nd user completed")
    y_is_3rd_user_completed = fields.Boolean(string="3rd user completed")
    y_approved_date1 = fields.Datetime("Approved Date 1")
    y_remarks = fields.Char(string="Remarks")

    y_approved_date2 = fields.Datetime("Approved Date 2")

    y_approved_date3 = fields.Datetime("Approved Date 3")

      

class SalesOrderApproval(models.Model):
    _name="sale.order.approval"
    _description  = 'sale.order.approval'

    y_approvals = fields.Selection(selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', 'All'),
            ('amount', 'Amount'),
            ],string='Approvals')
    y_is_approve = fields.Boolean("Approved")
    order_id = fields.Many2one('sale.order')
    y_user_ids= fields.Many2many('res.users', string='Users')
    y_amount = fields.Float("Amount")
    y_approved_date = fields.Datetime("Approved Date")
    y_remarks = fields.Char("Remarks")
    y_role = fields.Char("Role")
    y_approval_method = fields.Selection(selection=[
            ('stages', 'Stages'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount'),
            ],string='Approval Method')
    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")




class SalesLevelAmountApproval(models.Model):
    _name = "sale.lvlamt.approval"
    _description = "Sale Lvl&Amt Approval"

    def _group_internal_users(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    y_approval_level = fields.Selection(selection=[
            ('1stlvlapproval', '1 Level Approval'),
            ('2ndlvlapproval', '2 Level Approval'),
            ('3rdlvlapproval', '3 Level Approval'),
            ],string='Approval Level',copy=False,store=True)
    y_lvl1_user_ids = fields.Many2many("res.users",'lvl11_user',string="Level 1 User",domain=_group_internal_users)
    y_lvl2_user_ids = fields.Many2many("res.users",'lvl22_user',string="Level 2 User",domain=_group_internal_users)
    y_lvl3_user_ids = fields.Many2many("res.users",'lvl33_user',string="Level 3 User",domain=_group_internal_users)
    y_approval_amount_from = fields.Float("Amount(From)")
    y_approval_amount_to = fields.Float("Amount(To)")
    y_lvl_approval_id = fields.Many2one('sale.approval',string="Lvl and Approval")
    
    @api.constrains('y_approval_amount_from', 'y_approval_amount_to')
    def approval_lvl_amount_number(self):
        for rec in self:
            approval_lines = rec.y_lvl_approval_id.y_lvl_amt_approval_lines.sorted('id')
            if not approval_lines:
                raise UserError(_("Approval lines cannot be empty."))

            previous_to_amount = 0.0
            for index, line in enumerate(approval_lines):
                if line.y_approval_amount_from < 0 or line.y_approval_amount_to < 0:
                    raise UserError(_("Amount From ({}) and Amount To ({}) must not be less than 0."
                                      .format(line.y_approval_amount_from, line.y_approval_amount_to)))

                if index == 0:
                    if line.y_approval_amount_from < 0.0:
                        raise UserError(_("The first approval line must start from an Amount From of 0.0 or greater."))
                else:
                    if abs(line.y_approval_amount_from - (previous_to_amount + 0.01)) > 0.0001:
                        raise UserError(_("Amount From ({}) should be equal to the previous record Amount To ({}) plus 0.01."
                                          .format(line.y_approval_amount_from, previous_to_amount)))

                if line.y_approval_amount_to <= line.y_approval_amount_from:
                    raise UserError(_("Amount To ({}) should be greater than Amount From ({})."
                                      .format(line.y_approval_amount_to, line.y_approval_amount_from)))

                previous_to_amount = line.y_approval_amount_to

            if rec.y_approval_amount_from < 0.0:
                raise UserError(_("Amount From ({}) must not be less than 0.0."
                                  .format(rec.y_approval_amount_from)))

            if rec.y_approval_amount_to <= rec.y_approval_amount_from:
                raise UserError(_("Amount To ({}) should be greater than Amount From ({})."
                                  .format(rec.y_approval_amount_to, rec.y_approval_amount_from)))
    



class CustomizeSaleOrder(models.Model):
    _inherit = 'sale.order'

    y_so_approval_method = fields.Selection(selection=[
                ('stages', 'Stages'),
                ('amount', 'Amount'),
                ('lvlsamt','Levels & Amount'),
                ],string='Approval Method')


    




    y_sale_approval_line = fields.One2many("sale.order.approval",'order_id',copy=False)
    y_sale_lvl_amt_approval_line = fields.One2many("sale.order.approval.lvlsamt",'y_sale_lvl_id',copy=False)
    # max_approver = fields.Char(string="Approvers" ,compute="get_level_state")  
    y_max_approver = fields.Selection(selection=[('none',''),
            ('1stlvlapproval', '1 Level Approval'),
            ('2ndlvlapproval', '2 Level Approval'),
            ('3rdlvlapproval', '3 Level Approval'),],compute="get_level_state")

    y_approval_data = fields.Boolean("Data",store=True,copy=False)
    y_current_approvall = fields.Integer("Current Approval",default=1,copy=False)
    y_approval_method = fields.Char("Check Approval Method",copy=False)
    y_is_approved = fields.Boolean(string="Is Approved",copy=False, default=False)
    y_is_rejected = fields.Boolean(string="Is Rejected",copy=False)
    state = fields.Selection(selection_add=[
            ('reject', 'Rejected')
        ], ondelete={'reject': 'cascade'})

    y_to_approve_states = fields.Selection(selection=[
                ('to_approve_state1', '1st Approval Pending'),
                ('to_approve_state2', '2nd Approval Pending'),
                ('to_approve_state3', '3rd Approval Pending'),
                ('approved', 'Approved'),
                ('na','N/A'),
                ('not_applicable_for_approval','NAA'),
                ('reject','Rejected')
                ],string='To Approve State',default='na',store=True,copy=False)
    y_doc_type_id = fields.Many2one(tracking=True)

    y_to_approve_states_bool = fields.Boolean(string="Is states Bool")
    y_show_so_warning = fields.Char(string="Warning",compute=False,default=False,store=True)
    
   
    y_exchange_rate = fields.Float(string="Currency Rate",compute='_compute_exchange_rate',default=False,store=True,help="This rate will be used to convert the PO value and check the approval range in comapny currency.")
    
    @api.depends('y_doc_type_id')
    def _compute_exchange_rate(self):
        for rec in self:
            create_date_str = ''
            if rec.currency_id and rec.company_id.currency_id:
                if rec.currency_id.id != rec.company_id.currency_id.id:
                    if rec.create_date:
                        create_date_str = rec.create_date.strftime('%Y-%m-%d')
                        print("Create Date",create_date_str)
                    rate_found = False
                    for rate in rec.currency_id.rate_ids:
                        rate_date_str = rate.name.strftime('%Y-%m-%d')
                        print("Rate Date",rate_date_str)
                        if create_date_str == rate_date_str:
                            rec.y_exchange_rate = 1 / rate.company_rate
                            rate_found = True
                            break  
                    if not rate_found:
                        rec.y_exchange_rate = 1 / rec.currency_id.rate_ids[0].company_rate
                        print("Rate Found",rec.currency_id.rate_ids[0].company_rate)
                else:
                    rec.y_exchange_rate = 1
            else:
                rec.y_exchange_rate = 1
                
    @api.depends('order_line.price_unit', 'y_doc_type_id')
    def _compute_is_show_budget_warning_move(self):
        for rec in self:
            
            if rec.order_line:
                if rec.y_doc_type_id:
                    first_approval_amount = 0.0
                    last_line = self.env['sale.approval'].search([
                    ('y_document_type_id', '=', rec.y_doc_type_id.id)
                    ], limit=1)
                    if last_line and last_line.y_lvl_amt_approval_lines:
                        last_approval_amount = last_line.y_lvl_amt_approval_lines[-1].y_approval_amount_to
                        first_approval_amount = last_line.y_lvl_amt_approval_lines[0].y_approval_amount_from
                    else:
                        last_approval_amount = 0.0
                    if rec.amount_total > last_approval_amount and rec.currency_id == rec.company_id.currency_id:
                        message = f"The SO total amount {rec.amount_total} exceeds the approved limit {last_approval_amount}"
                        rec.y_show_so_warning = message
                    elif first_approval_amount > rec.amount_total and rec.currency_id == rec.company_id.currency_id:
                        message = f"The SO total amount {rec.amount_total} less then approved limit {first_approval_amount}"
                        rec.y_show_so_warning = message
                    elif (rec.amount_total * rec.y_exchange_rate) > last_approval_amount and rec.currency_id != rec.company_id.currency_id :
                        exchange_rate = rec.amount_total * rec.y_exchange_rate   
                        message = f"The SO total amount {exchange_rate}({rec.currency_id.symbol}{rec.amount_total}) exceeds the approved limit {last_approval_amount}"
                        rec.y_show_so_warning = message
                    elif first_approval_amount > (rec.amount_total * rec.y_exchange_rate) and rec.currency_id != rec.company_id.currency_id:
                        exchange_rate = rec.amount_total * rec.y_exchange_rate 
                        message = f"The SO total amount {exchange_rate}({rec.currency_id.symbol}{rec.amount_total}) less then approved limit {first_approval_amount}"
                        rec.y_show_so_warning = message
                    else:
                        rec.y_show_so_warning = False
                else:
                    rec.y_show_so_warning = False


    y_is_approval_req = fields.Boolean(string="Is Approval Request",store=True)

    y_is_1st_lvl_approval = fields.Boolean(string="Is 1st Level Approval")
    y_is_2nd_lvl_approval = fields.Boolean(string="Is 2nd Level Approval")
    y_is_3rd_lvl_approval = fields.Boolean(string="Is 3rd Level Approval")

    y_show_warning = fields.Boolean(string="Show Warning")
    y_approver_visible = fields.Boolean(string="Approver Visible",copy=False)
    
    def post_approval_message(self):
        if self.y_sale_lvl_amt_approval_line:
        
            for rec in self.y_sale_lvl_amt_approval_line:
                if rec.y_approval_level in ['1stlvlapproval', '2ndlvlapproval', '3rdlvlapproval']:
                    level = rec.y_approval_level.split('lvl')[0]
                    msg = f"Request Sent To {level} Level Approval"
                    
                    # Post the message to the record (optional)
                    self.message_post(body=msg)
                    email_template = self.env.ref('odoo_e_42.email_template_sale_approve').id
                    if email_template:
                        email_template_obj = self.env['mail.template'].browse(email_template)
                        for user_id in self.y_sale_lvl_amt_approval_line.y_lvl1_user_ids:
                            user = user_id
                            email_values = {
                                'email_to': user.login,
                                'email_from': self.user_id.login,
                                }
                            # print(email_values,'usere.rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr..1')  
                            email_template_obj.send_mail(self.id, email_values = email_values)

                            # Create mail activity only for users in y_lvl1_user_ids
                            if user_id:
                                type_id = self.env['mail.activity.type'].search([('name', '=', 'Sale Email')], limit=1)
                                res_model = self.env['ir.model'].sudo().search([('model', '=', 'sale.order')], limit=1)
                                subject = _('Sale Order Pending Approval')
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
        # else:
        #     raise UserError("The total amount is not within the approval grid")

    def request_for_approve(self):
        for rec in self:
            rec.y_approver_visible = True
            rec.y_to_approve_states = 'to_approve_state1'
            rec.post_approval_message()


    def action_draft(self):
        
        res = super(CustomizeSaleOrder, self).action_draft()
        if self.state == 'reject':
            self.state = 'draft'
            self.y_approver_visible = False
            self.y_sale_approval_line.unlink()
            self.y_sale_lvl_amt_approval_line.unlink()
            self.y_current_approvall = 1
            self._compute_lines_approved()
            self.request_for_approve()
        return res


  
    def get_level_state(self):
        for rec in self:
            if rec.y_sale_lvl_amt_approval_line:
                for rec2 in self.y_sale_lvl_amt_approval_line:
                    if rec2:
                        rec.y_max_approver = rec2.y_approval_level
                    else:

                        rec.y_max_approver = 'none'
            else:

                    rec.y_max_approver = 'none'

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
    #     res = super(CustomizeSalseOrder, self).get_view(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//field"):
    #             modifiers = json.loads(node.get("modifiers"))
    #             if type(modifiers.get('readonly')) == list:
    #                 modifiers['readonly'] = ['|'] + modifiers['readonly'] + [('state', '=', 'reject')]
    #             elif not type(modifiers.get('readonly')) == bool:
    #                 modifiers['readonly'] = [['state', '=', 'reject']]
    #             node.set("modifiers", json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc)
    #     return res


    # @api.depends('y_doc_type_id')
    def get_data(self):
        for each in self:
            each.y_approval_data = False
            each.y_sale_approval_line.unlink()
            each.y_sale_lvl_amt_approval_line.unlink()
            if each.y_approval_data == False:
                # each.y_approver_visible = True
                approval_ids = self.env['sale.approval'].search([('y_document_type_id','=',each.y_doc_type_id.id)])
                if approval_ids.y_approval_method in ('stages','amount'):
                    if each.y_sale_approval_line:
                        all_approvals = [x.y_is_approve for x in each.y_sale_approval_line]
                        if True in all_approvals:
                            raise UserError (_("You cannot change the document type once approved, Kindly Discard the PO and create a new PO"))
                        else:
                            each.y_sale_approval_line = False
                    approval_first_line = []
                    for each_line in approval_ids.y_approval_lines:
                        if approval_ids.y_approval_method == 'stages':
                            if each_line.y_approval_one:
                                value='1'
                            elif each_line.y_approval_two:
                                value='2'
                            elif each_line.y_approval_three:
                                value='3'
                            else:
                                value='4'
                        else:
                            value = 'amount'

                        valas = {
                            'y_approvals': value,
                            'y_user_ids': [(6, 0, each_line.y_user_ids.ids)],
                            'y_amount': each_line.y_approval_amount,
                            'y_approval_amount_from': each_line.y_approval_amount_from,
                            'y_approval_amount_to': each_line.y_approval_amount_to,
                            'y_role': each_line.y_role,
                            'order_id': each.id,
                            'y_approval_method': each_line.y_sale_approval_id.y_approval_method,
                        }

                        # Create sale order approval lines
                        y_sale_approved = self.env['sale.order.approval'].create(valas)
                        approval_first_line.append(y_sale_approved)
                        each.y_approval_method = approval_ids.y_approval_method

                    # Create mail activities for the first level only
                    first_level_approval = approval_first_line[0]
                    for user in first_level_approval.y_user_ids:
                        activity_type_id = self.env['mail.activity.type'].search([('name', '=', 'Sale Email')])
                        res_model = self.env['ir.model'].search([('model', '=', 'sale.order')])
                        subject = 'Sale Quotation Approval Request'
                        body = f'"{user.name}" requested an approval for the quotation "{each.name}"'
                        vals = {
                            'res_model_id': res_model.id,
                            'res_model': res_model.name,
                            'res_id': each.id,
                            'activity_type_id': activity_type_id.id,
                            'user_id': user.id,
                            'date_deadline': fields.Date.today(),
                            'summary': subject,
                            'note': body,
                        }
                        self.env['mail.activity'].create(vals)

                    # Post message
                    pending_state = get_selection_label(each, 'sale.order', 'y_to_approve_states', each.y_to_approve_states)
                    if each.y_approval_method == 'stages':
                        msg = f"{pending_state} By {', '.join(first_level_approval.y_user_ids.mapped('name'))}"
                    else:
                        new_ids = each.y_sale_approval_line.filtered(lambda line: int(line.y_approval_amount_from) <= each.amount_total and int(line.y_approval_amount_to) >= each.amount_total)
                        msg = f"{pending_state} By: {', '.join(new_ids.y_user_ids.mapped('name'))}"
                    each.message_post(body=msg)
                else:
                    
                    for each_line in approval_ids.y_lvl_amt_approval_lines:
                        val_from = [line.y_approval_amount_from for line in approval_ids.y_lvl_amt_approval_lines]
                        val_to = [line.y_approval_amount_to for line in approval_ids.y_lvl_amt_approval_lines]

                        if not val_from or not val_to:
                            continue

                        matching_line = None
                        amount_total = each.amount_total * each.y_exchange_rate if each.currency_id != each.company_id.currency_id else each.amount_total

                        # Adjust the first line's y_approval_amount_from for comparison only
                        adjusted_val_from = val_from[:]
                        adjusted_val_from[0] += 0.01

                        if adjusted_val_from[0] <= amount_total <= val_to[-1]:
                            for each_line in approval_ids.y_lvl_amt_approval_lines:
                                if each_line.y_approval_amount_from <= amount_total <= each_line.y_approval_amount_to:
                                    matching_line = each_line
                                    break

                        if matching_line:
                            vals = {
                                'y_approval_level': matching_line.y_approval_level,
                                'y_lvl1_user_ids': [(6, 0, matching_line.y_lvl1_user_ids.ids)],
                                'y_lvl2_user_ids': [(6, 0, matching_line.y_lvl2_user_ids.ids)],
                                'y_lvl3_user_ids': [(6, 0, matching_line.y_lvl3_user_ids.ids)],
                                'y_approval_amount_from': matching_line.y_approval_amount_from,
                                'y_approval_amount_to': matching_line.y_approval_amount_to,
                                'y_sale_lvl_id': each.id,
                            }
                            self.env['sale.order.approval.lvlsamt'].create(vals)
                            each.y_is_approval_req = False
                        else:
                            each.y_is_approval_req = True

                        each.y_is_1st_lvl_approval = any(line.y_lvl1_user_ids for line in each.y_sale_lvl_amt_approval_line)
                        each.y_is_2nd_lvl_approval = any(line.y_lvl2_user_ids for line in each.y_sale_lvl_amt_approval_line)
                        each.y_is_3rd_lvl_approval = any(line.y_lvl3_user_ids for line in each.y_sale_lvl_amt_approval_line)

                        each.y_approval_data = True
                        each.with_context(bypass_write=True).write({'y_approval_data': True})

                        return {
                            'type': 'ir.actions.client',
                            'tag': 'reload',
                        }
                
                
    @api.model
    def create(self, vals):
        record = super(CustomizeSaleOrder, self).create(vals)
        record.get_data()
        return record

    def write(self, vals):
        result = super(CustomizeSaleOrder, self).write(vals)
        fields_triggering_compute = ['y_doc_type_id', 'currency_id', 'amount_total', 'order_line']
        # print(fields_triggering_compute,'kkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
        if any(field in vals for field in fields_triggering_compute):
            self.with_context(bypass_write=True).get_data()

        return result

    # @api.depends('order_line.price_unit','order_line.product_uom_qty','order_line.tax_id','order_line.discount')
    # def onchange_compute_lines_approval_req(self):
    #     val_from = []
    #     val_to = []
    #     if self.sale_lvl_amt_approval_line != False:
    #         for rec in self.sale_lvl_amt_approval_line:
    #             val_from.append(rec.approval_amount_from)
    #             val_to.append(rec.approval_amount_to)

    #     if self.sale_lvl_amt_approval_line != False:
    #         for rec in self.sale_lvl_amt_approval_line:
    #             if self.amount_total < val_from[0] or self.amount_total > val_to[-1]:
    #                 self.is_approval_req = True
    #             else:
    #                 self.is_approval_req = False





    @api.onchange('y_doc_type_id')
    def _compute_lines_approved(self):
        if  self.y_doc_type_id.y_is_approval_required == True:
            self.y_is_approved = True
            approval_ids = self.env['sale.approval'].search([('y_document_type_id','=',self.y_doc_type_id.id)])
            # if not approval_ids:
            #     raise ValidationError("""Approvals Not Configured""")
            self.y_so_approval_method = approval_ids.y_approval_method
            self.y_to_approve_states = 'to_approve_state1'
        else:
            self.y_is_approved = False
        if self.y_doc_type_id.y_is_approval_required == False:
            self.y_to_approve_states = 'na'
        if self.y_doc_type_id.y_is_approval_required == True and self.y_approver_visible == False:
            print("APPROVER VISIBLE FALSE")
            self.y_to_approve_states = 'not_applicable_for_approval'
        
        


    def action_confirm(self):
        self.ensure_one()
        val_from = []
        val_to = []
        if self.y_sale_lvl_amt_approval_line != False:
            for rec in self.y_sale_lvl_amt_approval_line:
                val_from.append(rec.y_approval_amount_from)
                val_to.append(rec.y_approval_amount_to)
        if self.y_sale_approval_line and self.y_doc_type_id.y_is_approval_required == True:
            if self.y_approval_method == 'amount':
                all_approvals = [x.y_is_approve for x in self.y_sale_approval_line]
                if any(all_approvals) or self.y_sale_approval_line.filtered(lambda line : int(line.y_approval_amount_from) >= self.amount_total):
                    return super(CustomizeSaleOrder, self).action_confirm()
                # else:
                #     raise UserError (_("Sale Approval Pending"))
            elif self.y_approval_method == 'stages':
                all_approvals = [x.y_is_approve for x in self.y_sale_approval_line]
                # if False in all_approvals:
                #     raise UserError (_("Sale Approval Pending"))
                # else:
                return super(CustomizeSaleOrder, self).action_confirm()
        elif self.y_sale_lvl_amt_approval_line and self.y_doc_type_id.y_is_approval_required == True:

            approval_ids = self.env['sale.approval'].search([('y_document_type_id','=',self.y_doc_type_id.id)])

            if approval_ids.y_approval_method == 'lvlsamt':
                if self.amount_total < val_from[0] or self.amount_total > val_to[-1]:
                    return super(CustomizeSaleOrder, self).action_confirm()
                else:
                    all_approvals = [x.y_is_approval_completed for x in self.y_sale_lvl_amt_approval_line]
                    # if False in all_approvals:
                    #     raise UserError (_("Sales Approval Pending"))
                    # else:
                    return super(CustomizeSaleOrder, self).action_confirm()

        else:
            return super(CustomizeSaleOrder, self).action_confirm()
        


    
    def get_approval(self):
        current_user_id = self.env.uid
        user = self.env['res.users'].browse(current_user_id)
        approval_ids = self.env['sale.approval'].search([('y_document_type_id','=',self.y_doc_type_id.id)])
        current_appoval_line = False
        if approval_ids.y_approval_method in ('stages','amount'):
            for rec in approval_ids:
                if rec:
                    curr_method = rec.y_approval_method
                    all_approvals = [x.y_approvals for x in self.y_sale_approval_line]
                    if curr_method == 'stages':
                        current_appoval_line = self.y_sale_approval_line.filtered(lambda line : int(line.y_approvals) == self.y_current_approvall)

                        if current_appoval_line and current_appoval_line.y_user_ids:
                            if self.env.user.id in current_appoval_line.y_user_ids.ids :
                                current_appoval_line.y_is_approve = True
                                current_appoval_line.y_approved_date = datetime.now()
                                self.y_current_approvall += 1
                                
                                msg = """
                                         The Sale order has been approved by: %s
                                        """ % (user.name)
                                message_post = self.message_post(body=msg)

                                # Create mail.activity
                                
                                activity_type_id = self.env['mail.activity.type'].search([('name','=','Sale Email')])
                                res_model = self.env['ir.model'].sudo().search([('model','=','sale.order')])
                                subject = 'Sale Quotation Approval Request'
                                body = f'"{user.name}" has approved the quotation "{self.name}"'
                                for next_user in current_appoval_line.y_user_ids:
                                    activity_vals = {
                                        'res_model_id': res_model.id,
                                        'res_model': res_model.name,
                                        'res_id': self.id,
                                        'activity_type_id': activity_type_id.id,
                                        'user_id': next_user.id,
                                        'date_deadline': date.today(),
                                        'summary': subject,
                                        'note': body,
                                    }
                                    self.env['mail.activity'].create(activity_vals)

                                # Send email notification
                                email_template = self.env.ref('odoo_e_42.email_template_sale_approve')
                                if email_template:
                                    email_template.with_context({'record': self}).send_mail(self.id)

                            # else:
                            #     raise UserError (_(" You can't approve the order"))
                    
                    elif curr_method == 'amount':
                        if self.y_sale_approval_line.filtered(lambda line : int(line.y_approval_amount_from) <= self.amount_total):
                            new_ids = self.y_sale_approval_line.filtered(lambda line : int(line.y_approval_amount_from) <= self.amount_total and int(line.y_approval_amount_to) >= self.amount_total)
                            user_list = []

                            if new_ids:
                                for each in new_ids:
                                    if self.env.user.id in each.y_user_ids.ids:
                                        user_list.append(each)

                            if user_list:
                                user_list[0].y_is_approve = True

                                user_list[0].y_approved_date = datetime.now()
                                # self.action_confirm()

                                
                                msg = """
                                        The Sale order has been approved by: %s
                                        """ % (user.name)
                                message_post = self.message_post(body=msg)

                                # Create mail.activity
                                
                                activity_type_id = self.env['mail.activity.type'].search([('name','=','Sale Email')])
                                res_model = self.env['ir.model'].sudo().search([('model','=','sale.order')])
                                subject = 'Sale Quotation Approval Request'
                                body = f'"{user.name}" has approved the quotation "{self.name}"'
                                for next_user in user_list[0].y_user_ids:
                                    activity_vals = {
                                        'res_model_id': res_model.id,
                                        'res_model': res_model.name,
                                        'res_id': self.id,
                                        'activity_type_id': activity_type_id.id,
                                        'user_id': next_user.id,
                                        'date_deadline': date.today(),
                                        'summary': subject,
                                        'note': body,
                                    }
                                    self.env['mail.activity'].create(activity_vals)

                                # Send email notification
                                email_template = self.env.ref('odoo_e_42.email_template_sale_approve')
                                if email_template:
                                    email_template.with_context({'record': self}).send_mail(self.id)

                            # else:
                            #     raise UserError (_(" You can't approve the order"))

                        else:
                            self.action_confirm()
                # else:
                #     raise UserError (_(" Create the Sale approval "))
                    
            # for rec in self.y_sale_approval_line:
            #     if rec.y_is_approve==False and rec.y_approvals=='1':
            #         self.y_to_approve_states = 'to_approve_state2'
                    
            #         break

            #     if rec.y_is_approve==False and rec.y_approvals=='2' :
            #         self.y_to_approve_states = 'to_approve_state2'
            #         break

            #     if rec.y_is_approve==False and rec.y_approvals=='3' :
            #         self.y_to_approve_states = 'to_approve_state3'
            #         break

            #     data = self.y_sale_approval_line.mapped('y_is_approve')  
            #     if all(data) == True:
            #         self.y_to_approve_states = 'approved'
            #         self.action_confirm()
            #         break

        # -------------------------------------------------------------------------------------start
            if current_appoval_line and current_appoval_line.y_user_ids:
                pending_state = get_selection_label(self,'sale.order','y_to_approve_states',self.y_to_approve_states)
                if self.y_approval_method == 'stages':
                    msg = "{} By: {}".format(pending_state, ', '.join(current_appoval_line[0].y_user_ids.mapped('name')))
                    message_post = self.message_post(body=msg)

            self.action_confirm()

        # ---------------------------------------------------------------------------------------end
        else:
            for lvl_approval_lines in self.y_sale_lvl_amt_approval_line:

                if self.env.user.id in lvl_approval_lines.y_lvl1_user_ids.ids:
                    if not lvl_approval_lines.y_is_1st_user_completed:
                        lvl_approval_lines.y_is_1st_user_completed = True
                        lvl_approval_lines.y_approved_date1 = datetime.now()
        # ----------------------------------------------------------------start-----------------------------

                        first_approval_msg = """
                        First Approval Is Done: %s
                        """ % (self.env.user.name)
                        self.message_post(body=first_approval_msg)

                        email_template = self.env.ref('odoo_e_42.email_template_sale_approve').id
                        if email_template:
                            email_template_obj = self.env['mail.template'].browse(email_template)
                            for user_id in self.y_sale_lvl_amt_approval_line.y_lvl2_user_ids.ids:
                                user = self.env['res.users'].browse(user_id)
                                # print(user,'usere.rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr.........................................2222')  
                                email_values = {
                                    'email_to': user.login,
                                    'email_from': self.env.user.email,
                                    }
                                email_template_obj.send_mail(self.id, email_values = email_values)
                                print("approval,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",email_values)

                                # Create mail activity only for users in y_lvl1_user_ids
                                if user_id:
                                    type_id = self.env['mail.activity.type'].search([('name', '=', 'Sale Email')])
                                    res_model = self.env['ir.model'].sudo().search([('model', '=', 'sale.order')])
                                    subject = 'Sale Quotation Approval Request'
                                    body = f'"{user.name}" Requested an approval for the quotation "{self.name}"'
                                    vals = {
                                        'res_model_id': res_model.id,
                                        'res_model': res_model.name,
                                        'res_id': self.id,
                                        'activity_type_id': type_id.id,
                                        'user_id': user.id,
                                        'date_deadline': date.today(),
                                        'summary': subject,
                                        'note': html2plaintext(body)
                                    }
                                    activity = self.env['mail.activity'].create(vals)


                        if lvl_approval_lines.y_approval_level in ('2ndlvlapproval','3rdlvlapproval'):       
                           pending_state = get_selection_label(self,'sale.order','y_to_approve_states',self.y_to_approve_states)
                           msg = " Second Approval Is Pending By: {}".format(', '.join(lvl_approval_lines.y_lvl2_user_ids.mapped('name')))
                           message_post = self.message_post(body=msg)
# ----------------------------------------------------------------end-----------------------------

                    
                    
                    # elif lvl_approval_lines.y_is_1st_user_completed == True:

                    #     raise ValidationError("You have already approved at this Level.")
                    
                    # else:
                    #     raise UserError (_(" You can't approve the order"))
                



                if self.env.user.id in lvl_approval_lines.y_lvl2_user_ids.ids:
                    if lvl_approval_lines.y_is_1st_user_completed and not lvl_approval_lines.y_is_2nd_user_completed:
                        lvl_approval_lines.y_is_2nd_user_completed = True
                        lvl_approval_lines.y_approved_date2 = datetime.now()
# ----------------------------------------------------------------start-----------------------------

                        second_approval_msg = """
                         Second Approval Is Done: %s
                        """ % (self.env.user.name)
                        self.message_post(body=second_approval_msg)

                        email_template = self.env.ref('odoo_e_42.email_template_sale_approve').id
                        if email_template:
                            email_template_obj = self.env['mail.template'].browse(email_template)
                            for user_id in self.y_sale_lvl_amt_approval_line.y_lvl3_user_ids.ids:
                                user = self.env['res.users'].browse(user_id)
                                # print(user,'usere.rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr.........................................2222')  
                                email_values = {
                                    'email_to': user.login,
                                    'email_from': self.env.user.email,
                                    }
                                print("approval,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,1",email_values)
                                email_template_obj.send_mail(self.id, email_values = email_values)

                                # Create mail activity only for users in y_lvl1_user_ids
                                if user_id:
                                    type_id = self.env['mail.activity.type'].search([('name', '=', 'Sale Email')])
                                    res_model = self.env['ir.model'].sudo().search([('model', '=', 'sale.order')])
                                    subject = 'Sale Quotation Approval Request'
                                    body = f'"{user.name}" Requested an approval for the quotation "{self.name}"'
                                    vals = {
                                        'res_model_id': res_model.id,
                                        'res_model': res_model.name,
                                        'res_id': self.id,
                                        'activity_type_id': type_id.id,
                                        'user_id': user.id,
                                        'date_deadline': date.today(),
                                        'summary': subject,
                                        'note': html2plaintext(body)
                                    }
                                    activity = self.env['mail.activity'].create(vals)
                        if lvl_approval_lines.y_lvl3_user_ids:       
                            pending_state = get_selection_label(self,'sale.order','y_to_approve_states',self.y_to_approve_states)
                            msg = " Third Approval Is Pending By: {}".format(', '.join(lvl_approval_lines.y_lvl3_user_ids.mapped('name')))
                            message_post = self.message_post(body=msg)
# ----------------------------------------------------------------end-----------------------------

                    # elif lvl_approval_lines.y_is_1st_user_completed == True and lvl_approval_lines.y_is_1st_user_completed == True:
                    #     raise ValidationError("You have already approved at this Level.")
                    # else:
                    #     raise UserError (_(" You can't approve the order"))

                if self.env.user.id in lvl_approval_lines.y_lvl3_user_ids.ids:
                    if lvl_approval_lines.y_is_2nd_user_completed and not lvl_approval_lines.y_is_3rd_user_completed:
                        lvl_approval_lines.y_is_3rd_user_completed = True
                        lvl_approval_lines.y_approved_date3 = datetime.now()

                        third_approval_msg = """
                        Third Approval Is Done: %s
                        """ % (user.name)
                        self.message_post(body=third_approval_msg)
                    # elif lvl_approval_lines.y_is_1st_user_completed == True and lvl_approval_lines.y_is_1st_user_completed == True and lvl_approval_lines.y_is_3rd_user_completed == True:
                    #     raise ValidationError("You have already approved at this Level.")
                    # else:
                    #     raise UserError (_(" You can't approve the order"))



            self.action_confirm()

            for rec in self.y_sale_lvl_amt_approval_line:
                if rec.y_approval_level == '1stlvlapproval':
                    if rec.y_is_1st_user_completed==True:
                        rec.y_is_approval_completed = True
                        rec.y_sale_lvl_id.y_to_approve_states = 'approved'
                        self.action_confirm()

                if rec.y_approval_level == '2ndlvlapproval':
                    if rec.y_is_1st_user_completed==True and  rec.y_is_2nd_user_completed==True:
                        rec.y_is_approval_completed = True
                        rec.y_sale_lvl_id.y_to_approve_states = 'approved'
                        # self.state='sale'
                        self.action_confirm()

                if rec.y_approval_level == '3rdlvlapproval':
                    if rec.y_is_1st_user_completed==True and  rec.y_is_2nd_user_completed==True and rec.y_is_3rd_user_completed==True:
                        rec.y_is_approval_completed = True
                        rec.y_sale_lvl_id.y_to_approve_states = 'approved'
                        self.action_confirm()


            
# ----------------------------------------------------------------start-----------------------------
            # current_appoval_line = self.sale_approval_line.filtered(lambda line : int(line.approvals) == self.current_approvall)
            # self.current_approvall +=1
            # next_appoval_line = self.sale_approval_line.filtered(lambda line : int(line.approvals) == self.current_approvall)

            # pending_state = get_selection_label(self,'sale.order','to_approve_states',self.to_approve_states)
            # msg = "<div>{} is pending by: {}</div>".format(pending_state, ', '.join(next_appoval_line.user_ids.mapped('name')))
            # message_post = self.message_post(body=msg)
# ----------------------------------------------------------------end-----------------------------









                




           









                



            




   