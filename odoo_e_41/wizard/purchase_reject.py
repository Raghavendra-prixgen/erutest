# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context
import datetime
from datetime import date
from datetime import datetime


class Purchaseremarks(models.TransientModel):
    _name = 'purchase.approval.remarks'
    _description = 'purchase.approval.remarks'

    y_remarks = fields.Char( string='Remaks', required=True)

    def reject_order_mail(self, each, current_id):
        each.y_remarks = self.y_remarks
        current_id.state = 'reject'
        current_id.y_to_approve_states = 'reject'
        current_id.message_post(body=_("Reject Reason: %s ") % (self.y_remarks))

    def send_rejection_emails(self, each, current_id, user_lists):
        for user_list in user_lists:
            for user in user_list:
                mail_dict = {
                    "subject": 'Purchase Order Reject',
                    "email_from": self.env.user.name,
                    "email_to": user.name,
                    "recipient_ids": [(6, 0, [user.partner_id.id])],
                    "body_html": f"Hello, This Purchase Order {current_id.name} has been rejected."
                }
                if mail_dict:
                    mail_create = self.env['mail.mail'].sudo().create(mail_dict)
                    mail_create.send()
    
   

    def reject_order(self):
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)
        active_id =self.env.context['active_id']
        current_id=self.env['purchase.order'].search([('id','=',active_id)])
        if current_id.y_purchase_approval_line:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            for each in current_id.y_purchase_approval_line:
                if each.y_is_approve == False:
                    if current_id.y_approval_method == 'amount':
                        if self.env.user.id in each.y_user_ids.ids and  each.y_is_approve == False:
                            each.y_remarks = self.y_remarks
                            current_id.state = 'reject'
                            # current_id.y_to_approve_states = 'reject'
                            # each.is_email_sent = True
                            # for app_line in current_id.y_purchase_approval_line:
                            #     if app_line.is_email_sent == False and app_line.y_is_approve == True:
                            #         mail_dict = {
                            #         "subject": 'Purchase Order Reject',
                            #         "email_from": self.env.user.id,
                            #         "email_to": app_line.user_ids.name,
                            #         "recipient_ids": [(6,0, [app_line.user_ids.partner_id.id])],
                            #         "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            #         }
                            #         if mail_dict:
                            #             mail_create = self.env['mail.mail'].create(mail_dict)
                            #             mail_create.send()
                            if self.env.user.id != current_id.create_uid.id:
                                mail_dict = {
                                    "subject": 'Purchase Order Reject',
                                    "email_from": self.env.user.name,
                                    "email_to": current_id.create_uid.name,
                                    "recipient_ids": [(6,0, [current_id.create_uid.partner_id.id])],
                                    "body_html": "Hello, This Purchase Order {current_id.name} has been Rejected"
                                    }
                                if mail_dict:
                                    mail_create = self.env['mail.mail'].create(mail_dict)
                                    mail_create.send()
                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break
                    
                    elif current_id.y_approval_method == 'stages':
                        if (self.env.user.id in each.y_user_ids.ids and  each.y_is_approve == False ):
                            each.y_remarks = self.y_remarks
                            current_id.state = 'reject'
                            current_id.y_to_approve_states = 'reject'
                            each.y_is_email_sent = True
                            for app_line in current_id.y_purchase_approval_line:
                                print(app_line.y_user_ids.mapped('partner_id'),app_line.y_user_ids.mapped('name'),current_id,"CURRENT ID>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",current_id.y_to_approve_states)
                                if app_line.y_is_email_sent == False and app_line.y_is_approve == True:
                                    prt = [pr.partner_id.id for pr in app_line.y_user_ids]
                                    mail_dict = {
                                    "subject": 'Purchase Order Reject',
                                    "email_from": self.env.user.name,
                                    "email_to": app_line.y_user_ids.mapped('name'),
                                    "recipient_ids": [(6,0, prt)],
                                    "body_html": "Hello, This Purchase Order {current_id.name} has been Rejected"
                                    }
                                    if mail_dict:
                                        mail_create = self.env['mail.mail'].create(mail_dict)
                                        mail_create.send()
                                    if app_line.y_user_ids.ids != current_id.create_uid.id:

                                        mail_dict = {
                                            "subject": 'Purchase Order Reject',
                                            "email_from": self.env.user.name,
                                            "email_to": current_id.create_uid.name,
                                            "recipient_ids": [(6,0, [current_id.create_uid.partner_id.id])],
                                            "body_html": "Hello, This Purchase Order {current_id.name} has been Rejected"
                                            }
                                        if mail_dict:
                                            mail_create = self.env['mail.mail'].create(mail_dict)
                                            mail_create.send()
                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break

                    
        if current_id.y_purchase_lvl_amt_approval_line:
            print("##################################################3")
            for each in current_id.y_purchase_lvl_amt_approval_line:
                approval_ids = self.env['purchase.approval'].search([('y_document_type_id','=',current_id.y_doc_type_id.id)])
                if approval_ids.y_approval_method == 'lvlsamt':
                    if each.y_approval_level:
                        if each.y_approval_level == '1stlvlapproval':
                            print(4444444444444444444444444444444444444444444444)
                            # Check if the user is eligible to reject the order
                            if self.env.user.id in each.y_lvl1_user_ids.ids and not each.y_is_1st_user_completed:
                                print(8888888888888888888888888888888888888888888)
                                self.reject_order_mail(each, current_id)
                                break
                        elif each.y_approval_level == '2ndlvlapproval':
                            print(66666666666666666666666666666666666666)
                            # Check if the user is eligible to reject the order
                            if self.env.user.id in each.y_lvl2_user_ids.ids and not each.y_is_2nd_user_completed:
                                self.reject_order_mail(each, current_id)
                                # Send rejection emails to 1st level approvers
                                self.send_rejection_emails(each, current_id, [each.y_lvl1_user_ids])
                                break
                        elif each.y_approval_level == '3rdlvlapproval':
                            print(11111111111111111111111111111111111111111111111)
                            # Check if the user is eligible to reject the order
                            if self.env.user.id in each.y_lvl3_user_ids.ids and not each.y_is_3rd_user_completed:
                                print(33333333333333333333333333333333333333333333333333333333333333)
                                self.reject_order_mail(each, current_id)
                                # # Send rejection emails to 2nd and 1st level approvers
                                self.send_rejection_emails(each, current_id, [each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                                break
                        elif each.y_approval_level == '4thlvlapproval':
                            # Check if the user is eligible to reject the order
                            if self.env.user.id in each.y_lvl4_user_ids.ids and not each.y_is_4th_user_completed:
                                self.reject_order_mail(each, current_id)
                                # Send rejection emails to 3rd, 2nd, and 1st level approvers
                                self.send_rejection_emails(each, current_id, [each.y_lvl3_user_ids, each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                                break
                        elif each.y_approval_level == '5thlvlapproval':
                            # Check if the user is eligible to reject the order
                            if self.env.user.id in each.y_lvl5_user_ids.ids and not each.y_is_5th_user_completed:
                                self.reject_order_mail(each, current_id)
                                # Send rejection emails to 4th, 3rd, 2nd, and 1st level approvers
                                self.send_rejection_emails(each, current_id, [each.y_lvl4_user_ids, each.y_lvl3_user_ids, each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                                break
                        else:
                            raise UserError(_("You can't reject the order at this level"))
