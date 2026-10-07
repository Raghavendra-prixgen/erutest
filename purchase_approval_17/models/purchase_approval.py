# See LICENSE file for full copyright and licensing details.

from odoo import api, fields,models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date
from lxml import etree
import simplejson 
import json


class PurchaseDocType(models.Model):
    _inherit = 'purchase.doc.type'
    
    is_approval_required = fields.Boolean(default=True)


class PurchaseAppproval(models.Model):
    _name = "purchase.approval"
    _description ="purchase.approval"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    active = fields.Boolean(default=True)
    document_type_id = fields.Many2one("purchase.doc.type","Document Type",tracking=True)
    name = fields.Char("Name")
    warehouse_id = fields.Many2one("stock.warehouse","Warehouse",tracking=True)
    approval_lines = fields.One2many("purchase.approval.line","purchase_approval_id",tracking=True)
    lvl_amt_approval_lines = fields.One2many("purchase.lvlamt.approval","lvl_approval_id",tracking=True)

    approval_method = fields.Selection(selection=[
            
            ('stages', 'Levels'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount')
            ],string='Approval Method',default='amount',tracking=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)

    @api.constrains('name','company_id')
    def check_purchase_approval_name(self):
        for rec in self:
            docs=rec.env['purchase.approval'].search([('name','=',rec.name),('company_id','=',rec.company_id.id)])
            if len(docs) > 1:
                raise ValidationError(_("""name already exists!"""))

    @api.onchange('document_type_id')
    def _update_name(self):
        if self.document_type_id:
            self.name = self.document_type_id.y_name

    @api.constrains('document_type_id', 'warehouse_id')
    def _check_duplicate(self):
        existing_id=self.env['purchase.approval'].search([
                                            ('document_type_id','=',self.document_type_id.id),
                                            ("warehouse_id",'=',self.warehouse_id.id),
                                            ])
        if not len(existing_id) ==1:
            raise UserError (_("You Can't create the Purchase Approval from the same Warehouse and Document Type"))


class PurchaseAppprovalLine(models.Model):
    _name = "purchase.approval.line"
    _description ="purchase.approval.line"

    def _group_internal_users(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []


    user_ids = fields.Many2many("res.users",string="Users",domain=_group_internal_users)
    purchase_approval_id = fields.Many2one("purchase.approval",string="Appove")
    approval_amount = fields.Float("Amount(UP To)")
    approval_amount_from = fields.Float("Amount(From)")
    approval_amount_to = fields.Float("Amount(To)")


    approval_one= fields.Boolean("1")
    approval_two= fields.Boolean("2")
    approval_three= fields.Boolean("3")
    approval_all= fields.Boolean("Parallel")
    role = fields.Char("Role")


    @api.onchange('approval_all')
    def _update_approval_all(self):
        if self.approval_all:
            self.approval_one = False
            self.approval_two = False
            self.approval_three = False
    @api.onchange('approval_one')
    def _update_approval_one(self):
        if self.approval_one:
            self.approval_two = False
            self.approval_three = False
            self.approval_all = False

    @api.onchange('approval_two')
    def _update_approval_two(self):
        if self.approval_two:
            self.approval_one = False
            self.approval_three = False
            self.approval_all = False

    @api.onchange('approval_three')
    def _update_approval_three(self):
        if self.approval_three:
            self.approval_one = False
            self.approval_two = False
            self.approval_all = False

    

    @api.constrains('approval_amount_from')
    def approval_amount_number(self):
        total_approval = self.purchase_approval_id.approval_lines.mapped('id')
        purchase_approval_line_obj = self.env['purchase.approval.line'].browse(total_approval[-2:-1])
        for rec in self:
             if rec.approval_amount_from < purchase_approval_line_obj.approval_amount_to:
                 raise UserError(_("Amount(From) should be greater than previous record Amount(To)"))
             if rec.approval_amount_to < rec.approval_amount_from:
                 raise UserError(_("Amount(To) is less than Amount(From)"))

    @api.constrains('approval_amount_from','approval_amount_to')
    def approval_amount_number(self):
        total_approval = self.purchase_approval_id.approval_lines.mapped('id')
        purchase_approval_line_obj = self.env['purchase.approval.line'].browse(total_approval[-2:-1])
        for rec in self:

            if rec.approval_amount_from < purchase_approval_line_obj.approval_amount_to:
                raise UserError(_("Amount(From) should be greater than previous record Amount(To)"))
            if rec.approval_amount_to < rec.approval_amount_from:
                raise UserError(_("Amount(To) is less than Amount(From)"))

class PurchaseOrderApprovalLvlAmt(models.Model):
    _name="purchase.order.approval.lvlsamt"
    _description  = 'purchase.order.approval Lvl Amt'

    approval_level = fields.Selection(selection=[
            ('1stlvlapproval', '1 Level Approval'),
            ('2ndlvlapproval', '2 Level Approval'),
            ('3rdlvlapproval', '3 Level Approval'),
            ],string='Approval Level',copy=False)
    lvl1_user_ids = fields.Many2many("res.users",'lvl4_user',string="Level 1 User")
    lvl2_user_ids = fields.Many2many("res.users",'lvl5_user',string="Level 2 User")
    lvl3_user_ids = fields.Many2many("res.users",'lvl6_user',string="Level 3 User")
    approval_amount_from = fields.Float("Amount(From)")
    approval_amount_to = fields.Float("Amount(To)")
    purchase_lvl_id = fields.Many2one('purchase.order')
    is_approval_completed = fields.Boolean(default=False)
    is_1st_user_completed = fields.Boolean(string="1st user completed")
    is_2nd_user_completed = fields.Boolean(string="2nd user completed")
    is_3rd_user_completed = fields.Boolean(string="3rd user completed")
    approved_date1 = fields.Datetime("Approved Date 1")
    remarks = fields.Char(string="Remarks")

    approved_date2 = fields.Datetime("Approved Date 2")

    approved_date3 = fields.Datetime("Approved Date 3")

class PurchaseOrderApproval(models.Model):
    _name="purchase.order.approval"
    _description  = 'purchase.order.approval'

    approvals = fields.Selection(selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', 'All'),
            ('amount', 'Amount'),
            ],string='Approvals')
    is_approve = fields.Boolean("Approved")
    order_id = fields.Many2one('purchase.order')
    user_ids= fields.Many2many('res.users', string='Users')
    amount = fields.Float("Amount")
    approved_date = fields.Datetime("Approved Date")
    remarks = fields.Char("Remarks")
    role = fields.Char("Role")
    approval_method = fields.Selection(selection=[
            ('stages', 'Stages'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount'),
            ],string='Approval Method')
    approval_amount_from = fields.Float("Amount(From)")
    approval_amount_to = fields.Float("Amount(To)")
    is_email_sent = fields.Boolean(string="Is Email Sent")



    
class PurchaseLevelAmmountApproval(models.Model):
    _name = "purchase.lvlamt.approval"
    _description = "Purchase Lvl&Amt Approval"

    def _group_internal_users(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    approval_level = fields.Selection(selection=[
            ('1stlvlapproval', '1 Level Approval'),
            ('2ndlvlapproval', '2 Level Approval'),
            ('3rdlvlapproval', '3 Level Approval'),
            ],string='Approval Level',copy=False)
    lvl1_user_ids = fields.Many2many("res.users",'lvl1_user',string="Level 1 User",domain=_group_internal_users)
    lvl2_user_ids = fields.Many2many("res.users",'lvl2_user',string="Level 2 User",domain=_group_internal_users)
    lvl3_user_ids = fields.Many2many("res.users",'lvl3_user',string="Level 3 User",domain=_group_internal_users)
    approval_amount_from = fields.Float("Amount(From)")
    approval_amount_to = fields.Float("Amount(To)")
    lvl_approval_id = fields.Many2one('purchase.approval',string="Lvl and Approval")

    @api.constrains('approval_amount_from','approval_amount_to')
    def approval_lvl_amount_number(self):
        filterd_ids = self.lvl_approval_id.lvl_amt_approval_lines
        for record in filterd_ids:
            if record != filterd_ids[0]:
                filterd_line_ids = filterd_ids.mapped('id')
                approval_line_id = record.env['purchase.lvlamt.approval'].browse(filterd_line_ids[filterd_line_ids.index(record.id)-1])
                if record.approval_amount_from <= approval_line_id.approval_amount_to:
                    raise UserError(_("Amount From({}) should be greater than previous record Amount To({})".format(record.approval_amount_from,approval_line_id.approval_amount_to)))
        for rec in self:
            if rec.approval_amount_to <= rec.approval_amount_from:
                raise UserError(_("Amount To ({}) is less than Amount From ({})".format(rec.approval_amount_to,rec.approval_amount_from)))

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    approved_by = fields.Many2one('res.users' , string='Approved By')
    approve_doc = fields.Boolean('Approve Doc',copy=False)

    po_approval_method = fields.Selection(selection=[
            ('stages', 'Level'),
            ('amount', 'Amount'),
            ('lvlsamt','Levels & Amount'),
            ],string='Approval Method')


    purchase_approval_line = fields.One2many("purchase.order.approval",'order_id',copy=False)
    purchase_lvl_amt_approval_line = fields.One2many("purchase.order.approval.lvlsamt",'purchase_lvl_id',copy=False)


    approval_data = fields.Boolean("Data",compute ="get_data",store=True,copy=False)
    current_approvall = fields.Integer("Current Approval",default=1,copy=False)
    approval_method = fields.Char("Approval Method",copy=False)
    is_approved = fields.Boolean(copy=False,default=False)
    is_rejected = fields.Boolean(copy=False)
    state = fields.Selection(selection_add=[
            ('reject', 'Rejected')
        ], ondelete={'reject': 'cascade'})

    to_approve_states = fields.Selection(selection=[
            
            ('to_approve_state1', '1st Approval Pending'),
            ('to_approve_state2', '2nd Approval Pending'),
            ('to_approve_state3', '3rd Approval Pending'),
            ('approved', 'Approved'),
            ('na','N/A'),
            ('reject','Rejected')
            ],string='To Approve State',default='na',store=True,copy=False)


    to_approve_states_bool = fields.Boolean(string="Is states Bool")

    is_approval_req = fields.Boolean(store=True)

    is_1st_lvl_approval = fields.Boolean()
    is_2nd_lvl_approval = fields.Boolean()
    is_3rd_lvl_approval = fields.Boolean()

    show_warning = fields.Boolean()
    product_ids = fields.Many2many('product.product', string="Products")

    # is_approval_req = fields.Boolean(compute='onchange_compute_POL_approval_req', store=True)

    def get_set_draft(self):
        if self.state == 'reject':
            self.state = 'draft'
            self.y_doc_type_id = False
            approval_obj = self.env['purchase.order.approval.lvlsamt'].search([('purchase_lvl_id', '=', self.id)]).unlink()
            approval_order_obj = self.env['purchase.order.approval'].search([('order_id', '=', self.id)]).unlink()
            self.current_approvall = 1
            print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", approval_obj)

    @api.onchange('y_doc_type_id')
    def get_doc_product(self):
        if self.y_doc_type_id:
            product_obj = self.env['product.product'].search([])
            product_list = []
            for product in product_obj:
                if self.y_doc_type_id in product.product_tmpl_id.y_doc_type_ids:
                    product_list.append(product.id)
            self.product_ids = product_list


    def button_draft(self):
        res = super().button_draft()
        self.purchase_approval_line.unlink()
        self.purchase_lvl_amt_approval_line.unlink()
        self._compute_lines_approved()
        self.get_data()




    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu,)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field"):
                modifiers = json.loads(node.get("modifiers"))
                if type(modifiers.get('readonly')) == list:
                    modifiers['readonly'] = ['|'] + modifiers['readonly'] + [('state', '=', 'reject')]
                elif not type(modifiers.get('readonly')) == bool:
                    modifiers['readonly']=[['state', '=', 'reject']]
                    node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc)
        return res


    @api.depends('picking_type_id','y_doc_type_id')
    def get_data(self):
        for each in self:
            if each.picking_type_id.id and each.approval_data == False:
                approval_ids = self.env['purchase.approval'].search([('document_type_id','=',each.y_doc_type_id.id)])
                if approval_ids.approval_method in ('stages','amount'):
                    if self.purchase_approval_line:
                            all_approvals = [x.is_approve for x in self.purchase_approval_line]
                            if True in all_approvals:
                                raise UserError (_("Oops!!!!You cannot change the document type once approved, Kindly Discard the PO and create a new PO"))
                            else:
                                self.purchase_approval_line = False

                    for each_line in approval_ids.approval_lines:
                        if approval_ids.approval_method == 'stages':
                            if each_line.approval_one:
                                value='1'
                            elif each_line.approval_two:
                                value='2'
                            elif each_line.approval_three:
                                value='3'
                            else:
                                value='4'
                        else:
                            value = 'amount'

                        valas={
                        'approvals':value ,
                        'user_ids': [(6, 0, each_line.user_ids.ids)],
                        'amount':each_line.approval_amount,
                        'approval_amount_from':each_line.approval_amount_from,
                        'approval_amount_to':each_line.approval_amount_to,
                        'role':each_line.role,
                        'order_id':each.id,
                        'approval_method':each_line.purchase_approval_id.approval_method,
                        }
                        self.env['purchase.order.approval'].create(valas)
                        each.approval_method = approval_ids.approval_method
                else:
                    
                    for each_line in approval_ids.lvl_amt_approval_lines:
                        val_from = []
                        val_to = []
                        for rec in approval_ids.lvl_amt_approval_lines:
                            val_from.append(rec.approval_amount_from)
                            val_to.append(rec.approval_amount_to)
                        if val_from[0] < self.amount_total or self.amount_total > val_to[-1]:
                            if each_line.filtered(lambda line : int(line.approval_amount_from) <= each.amount_total and int(line.approval_amount_to) >= each.amount_total):
                                val = each_line.filtered(lambda line : int(line.approval_amount_from) <= each.amount_total and int(line.approval_amount_to) >= each.amount_total)
                                # print(each_line.filtered(lambda line : int(line.approval_amount_from) <= each.amount_total and int(line.approval_amount_to) >= each.amount_total))
                                print("Im from IF________________________________________________________________________________")
                                print("\n"*25)
                                valas={
                                'approval_level':val.approval_level,
                                'lvl1_user_ids': [(6, 0, val.lvl1_user_ids.ids)],
                                'lvl2_user_ids': [(6, 0, val.lvl2_user_ids.ids)],

                                'lvl3_user_ids': [(6, 0, val.lvl3_user_ids.ids)],
                                'approval_amount_from':val.approval_amount_from,
                                'approval_amount_to':val.approval_amount_to,
                                'purchase_lvl_id':each.id,
                                }
                                self.env['purchase.order.approval.lvlsamt'].create(valas)
                                self.is_approval_req = False
                        else:
                            # print(each_line.filtered(lambda line : int(line.approval_amount_from) <= each.amount_total and int(line.approval_amount_to) >= each.amount_total))
                            print("Im from ELSE________________________________________________________________________________")
                            print("\n"*25)
                            valas={
                            'approval_level':each_line.approval_level,
                            'lvl1_user_ids': [(6, 0, each_line.lvl1_user_ids.ids)],
                            'lvl2_user_ids': [(6, 0, each_line.lvl2_user_ids.ids)],

                            'lvl3_user_ids': [(6, 0, each_line.lvl3_user_ids.ids)],
                            'approval_amount_from':each_line.approval_amount_from,
                            'approval_amount_to':each_line.approval_amount_to,
                            'purchase_lvl_id':each.id,
                            }
                            self.env['purchase.order.approval.lvlsamt'].create(valas)   
                            self.is_approval_req = True                         
                        
                   
                    if each.purchase_lvl_amt_approval_line.lvl1_user_ids:
                        each.is_1st_lvl_approval = True

                    if each.purchase_lvl_amt_approval_line.lvl2_user_ids:
                        each.is_2nd_lvl_approval = True

                    if each.purchase_lvl_amt_approval_line.lvl3_user_ids:
                        each.is_3rd_lvl_approval = True



    @api.onchange('y_doc_type_id')
    def _compute_lines_approved(self):
        if  self.y_doc_type_id.is_approval_required == True:
            self.is_approved = True
            approval_ids = self.env['purchase.approval'].search([('document_type_id','=',self.y_doc_type_id.id)])
            if not approval_ids:
                raise ValidationError("""Approvals Not Configured""")
            self.po_approval_method = approval_ids.approval_method
            self.to_approve_states = 'to_approve_state1'
        else:
            self.is_approved = False
        if self.y_doc_type_id.is_approval_required == False:
            self.to_approve_states = 'na'



        
    def button_confirm(self):
        self.ensure_one()
        val_from = []
        val_to = []
        if self.purchase_lvl_amt_approval_line != False:
            for rec in self.purchase_lvl_amt_approval_line:
                val_from.append(rec.approval_amount_from)
                val_to.append(rec.approval_amount_to)
        if self.purchase_approval_line and self.y_doc_type_id.is_approval_required == True:
            if self.approval_method == 'amount':
                all_approvals = [x.is_approve for x in self.purchase_approval_line]
                if any(all_approvals) or self.purchase_approval_line.filtered(lambda line : int(line.approval_amount_from) >= self.amount_total):
                    return super(PurchaseOrder, self).button_confirm()
                else:
                    raise UserError (_("Purchase Approval Pending"))
            elif self.approval_method == 'stages':
                all_approvals = [x.is_approve for x in self.purchase_approval_line]
                if False in all_approvals:
                    raise UserError (_("Purchase Approval Pending"))
                else:
                    return super(PurchaseOrder, self).button_confirm()
        elif self.purchase_lvl_amt_approval_line and self.y_doc_type_id.is_approval_required == True:

            approval_ids = self.env['purchase.approval'].search([('document_type_id','=',self.y_doc_type_id.id)])

            if approval_ids.approval_method == 'lvlsamt':
                if self.amount_total < val_from[0] or self.amount_total > val_to[-1]:
                    return super(PurchaseOrder, self).button_confirm()
                else:
                    all_approvals = [x.is_approval_completed for x in self.purchase_lvl_amt_approval_line]
                    if False in all_approvals:
                        raise UserError (_("Purchase Approval Pending"))
                    else:
                        return super(PurchaseOrder, self).button_confirm()

        else:
            return super(PurchaseOrder, self).button_confirm()



    def get_approval(self):
        current_user_id = self.env.uid
        self.approved_by = current_user_id
        print(self.approve_doc,9999999999999999999999999999999999999)
        user = self.env['res.users'].browse(current_user_id)
        approval_ids = self.env['purchase.approval'].search([('document_type_id','=',self.y_doc_type_id.id)])
        if approval_ids.approval_method in ('stages','amount'):
            for rec in approval_ids:
                if rec:
                    curr_method = rec.approval_method
                    all_approvals = [x.approvals for x in self.purchase_approval_line]
                    if curr_method == 'stages':
                        current_appoval_line = self.purchase_approval_line.filtered(lambda line : int(line.approvals) == self.current_approvall)
                        if current_appoval_line:
                            if self.env.user.id in current_appoval_line.user_ids.ids :
                                current_appoval_line.is_approve = True
                                current_appoval_line.approved_date = datetime.now()
                                self.current_approvall +=1
                                self.approve_doc = True

                                
                                msg = """
                                        <div> The purchase order has been approved by: %s</div>
                                        """%(user.name)
                                self.message_post(body=msg)
                                
                            else:
                                raise UserError (_("Oops!!!! You can't approve the order"))
                    
                    elif curr_method == 'amount':
                        if self.purchase_approval_line.filtered(lambda line : int(line.approval_amount_from) <= self.amount_total):
                            new_ids = self.purchase_approval_line.filtered(lambda line : int(line.approval_amount_from) <= self.amount_total and int(line.approval_amount_to) >= self.amount_total)
                            user_list =[]
                            for each in new_ids:
                                if self.env.user.id in each.user_ids.ids:
                                    user_list.append(each)
                            if user_list:
                                user_list[0].is_approve = True
                                self.approve_doc = True

                                user_list[0].approved_date = datetime.now()
                                self.button_confirm()
                            else:
                                raise UserError (_("Oops!!!! You can't approve the order"))
                        else:
                            self.button_confirm()
                else:
                    raise UserError (_("Oops!!!! Create the purchase approval "))
            for rec in self.purchase_approval_line:
                if rec.is_approve==False and rec.approvals=='1':
                    self.to_approve_states = 'to_approve_state2'
                    break

                if rec.is_approve==False and rec.approvals=='2' :
                    self.to_approve_states = 'to_approve_state2'
                    break

                if rec.is_approve==False and rec.approvals=='3' :
                    self.to_approve_states = 'to_approve_state3'
                    break


                data = self.purchase_approval_line.mapped('is_approve')  
                if all(data) == True:
                    self.to_approve_states = 'approved'
                    self.button_confirm()
                    break
        else:
            for lvl_approval_lines in self.purchase_lvl_amt_approval_line:
                if self.env.user.id in lvl_approval_lines.lvl1_user_ids.ids:
                    lvl_approval_lines.is_1st_user_completed = True
                    
                    print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS", lvl_approval_lines.is_1st_user_completed)
                    lvl_approval_lines.approved_date1 = datetime.now()
                    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", lvl_approval_lines.approved_date1)
                    self.approve_doc = True



                if self.env.user.id in lvl_approval_lines.lvl2_user_ids.ids :
                    lvl_approval_lines.is_2nd_user_completed = True
                    lvl_approval_lines.approved_date2 = datetime.now()


                if self.env.user.id in lvl_approval_lines.lvl3_user_ids.ids :
                    lvl_approval_lines.is_3rd_user_completed = True
                    lvl_approval_lines.approved_date3 = datetime.now()



            for rec in self.purchase_lvl_amt_approval_line:
                if rec.approval_level == '1stlvlapproval':
                    if rec.is_1st_user_completed==True:
                        rec.is_approval_completed = True
                        self.approve_doc = True

                        self.button_confirm()


                if rec.approval_level == '2ndlvlapproval':
                    if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==True:
                        rec.is_approval_completed = True

                        self.button_confirm()
                        # self.state='purchase'

                if rec.approval_level == '3rdlvlapproval':
                    if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==True and rec.is_3rd_user_completed==True:
                        rec.is_approval_completed = True
                        self.button_confirm()


            for rec in self.purchase_lvl_amt_approval_line:
                if rec.approval_level == '2ndlvlapproval':
                    if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==False:
                        self.approve_doc = True

                        self.to_approve_states = 'to_approve_state2'

                if rec.approval_level == '3rdlvlapproval':
                    if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==False and rec.is_3rd_user_completed==False:
                        self.to_approve_states = 'to_approve_state2'

                    if rec.is_1st_user_completed==True and  rec.is_2nd_user_completed==True and rec.is_3rd_user_completed==False:
                        self.to_approve_states = 'to_approve_state3'

class onchangefuncforPOl(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('price_unit')
    def newonchange_POL_is_approval_req(self):
        # self.env['purchase.order'].get_data()
        print("Im from Before Onchange_________________________________________________________","\n"*25)
        self.order_id.get_data()
        print("Im from After Onchange_________________________________________________________","\n"*25)
