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
        current_id.to_approve_states = 'reject'
        current_id.message_post(body=_("Reject Reason: %s ") % (self.y_remarks))

    def send_rejection_emails(self, each, current_id, user_lists):
        for user_list in user_lists:
            for user in user_list:
                mail_dict = {
                    "subject": 'Purchase Order Reject',
                    "email_from": self.env.user.id,
                    "email_to": user.name,
                    "recipient_ids": [(6, 0, [user.partner_id.id])],
                    "body_html": f"Hello, This Purchase Order {current_id.name} has been rejected."
                }
                if mail_dict:
                    mail_create = self.env['mail.mail'].create(mail_dict)
                    mail_create.send()
    
   

    def reject_order(self):
        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)
        active_id =self.env.context['active_id']
        current_id=self.env['purchase.order'].search([('id','=',active_id)])
        if current_id.y_purchase_approval_line:
            for each in current_id.y_purchase_approval_line:
                if each.y_is_approve == False:
                    if current_id.y_approval_method == 'amount':
                        if self.env.user.id in each.user_ids.ids and  each.y_is_approve == False:
                            each.y_remarks = self.y_remarks
                            current_id.state = 'reject'
                            # current_id.to_approve_states = 'reject'
                            # each.y_is_email_sent = True
                            # for app_line in current_id.purchase_approval_line:
                            #     if app_line.y_is_email_sent == False and app_line.is_approve == True:
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
                                    "email_from": self.env.user.id,
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
                                if app_line.y_is_email_sent == False and app_line.y_is_approve == True:
                                    mail_dict = {
                                    "subject": 'Purchase Order Reject',
                                    "email_from": self.env.user.id,
                                    "email_to": app_line.y_user_ids.name,
                                    "recipient_ids": [(6,0, [app_line.y_user_ids.partner_id.id])],
                                    "body_html": "Hello, This Purchase Order {current_id.name} has been Rejected"
                                    }
                                    if mail_dict:
                                        mail_create = self.env['mail.mail'].create(mail_dict)
                                        mail_create.send()
                                    if app_line.user_ids.id != current_id.create_uid.id:
                                        mail_dict = {
                                            "subject": 'Purchase Order Reject',
                                            "email_from": self.env.user.id,
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
            for each in current_id.y_purchase_lvl_amt_approval_line:
                approval_ids = self.env['purchase.approval'].search([('y_document_type_id','=',current_id.y_doc_type_id.id)])
                if approval_ids.y_approval_method == 'lvlsamt':
                    if each.y_approval_level in ['1stlvlapproval', '2ndlvlapproval', '3rdlvlapproval', '4thlvlapproval', '5thlvlapproval']:
                        if self.env.user.id in each.y_lvl1_user_ids.ids and not each.y_is_1st_user_completed:
                            self.reject_order_mail(each, current_id)
                            if each.y_approval_level == '2ndlvlapproval':
                                self.send_rejection_emails(each, current_id, [each.y_lvl1_user_ids])
                            elif each.y_approval_level == '3rdlvlapproval':
                                self.end_rejection_emails(each, current_id, [each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                            elif each.y_approval_level == '4thlvlapproval':
                                self.send_rejection_emails(each, current_id, [each.y_lvl3_user_ids, each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                            elif each.y_approval_level == '5thlvlapproval':
                                self.send_rejection_emails(each, current_id, [each.y_lvl4_user_ids, each.y_lvl3_user_ids, each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                            break
                        elif self.env.user.id in each.y_lvl2_user_ids.ids and not each.is_2nd_user_completed:
                            self.reject_order_mail(each, current_id)
                            if each.y_approval_level in ['3rdlvlapproval', '4thlvlapproval', '5thlvlapproval']:
                                self.send_rejection_emails(each, current_id, [each.y_lvl1_user_ids])
                            break
                        elif self.env.user.id in each.y_lvl3_user_ids.ids and not each.is_3rd_user_completed:
                            self.reject_order_mail(each, current_id)
                            if each.y_approval_level in ['4thlvlapproval', '5thlvlapproval']:
                                self.send_rejection_emails(each, current_id, [each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                            break
                        elif self.env.user.id in each.y_lvl4_user_ids.ids and not each.y_is_4th_user_completed:
                            self.reject_order_mail(each, current_id)
                            if each.y_approval_level == '5thlvlapproval':
                                self.send_rejection_emails(each, current_id, [each.y_lvl3_user_ids, each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                            break
                        elif self.env.user.id in each.y_lvl5_user_ids.ids and not each.y_is_5th_user_completed:
                            self.reject_order_mail(each, current_id)
                            break
                    else:
                        raise UserError(_("You can't reject the order"))
