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

    remarks = fields.Char( string='Remaks', required=True)
    
   

    def reject_order(self):
        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)
        active_id =self.env.context['active_id']
        current_id=self.env['purchase.order'].search([('id','=',active_id)])
        if current_id.purchase_approval_line:
            for each in current_id.purchase_approval_line:
                if each.is_approve == False:
                    if current_id.approval_method == 'amount':
                        if self.env.user.id in each.user_ids.ids and  each.is_approve == False:
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'
                            # each.is_email_sent = True
                            # for app_line in current_id.purchase_approval_line:
                            #     if app_line.is_email_sent == False and app_line.is_approve == True:
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
                                    "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                                    }
                                if mail_dict:
                                    mail_create = self.env['mail.mail'].create(mail_dict)
                                    mail_create.send()
                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break
                    
                    elif current_id.approval_method == 'stages':
                        if (self.env.user.id in each.user_ids.ids and  each.is_approve == False ):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'
                            each.is_email_sent = True
                            for app_line in current_id.purchase_approval_line:
                                if app_line.is_email_sent == False and app_line.is_approve == True:
                                    mail_dict = {
                                    "subject": 'Purchase Order Reject',
                                    "email_from": self.env.user.id,
                                    "email_to": app_line.user_ids.name,
                                    "recipient_ids": [(6,0, [app_line.user_ids.partner_id.id])],
                                    "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
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
                                            "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                                            }
                                        if mail_dict:
                                            mail_create = self.env['mail.mail'].create(mail_dict)
                                            mail_create.send()
                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break

                    
        if current_id.purchase_lvl_amt_approval_line:
            for each in  current_id.purchase_lvl_amt_approval_line:
 
                approval_ids = self.env['purchase.approval'].search([('document_type_id','=',current_id.y_doc_type_id.id)])

                if approval_ids.approval_method == 'lvlsamt':
                    if each.approval_level == '1stlvlapproval':

                        if (self.env.user.id in each.lvl1_user_ids.ids and  each.is_1st_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))
                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break

                    if each.approval_level == '2ndlvlapproval':
                        if (self.env.user.id in each.lvl1_user_ids.ids and  each.is_1st_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))
                            # each.is_email_sent = True
                            # mail_dict = {
                            # "subject": 'Purchase Order Reject',
                            # "email_from": self.env.user.id,
                            # "email_to": each.lvl2_user_ids.name,
                            # "recipient_ids": [(6,0, [each.lvl2_user_ids.partner_id.id])],
                            # "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            # }
                            # if mail_dict:
                            #     mail_create = self.env['mail.mail'].create(mail_dict)
                            #     mail_create.send()
                            break

                        if (self.env.user.id in each.lvl2_user_ids.ids and  each.is_2nd_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))
                            mail_dict = {
                            "subject": 'Purchase Order Reject',
                            "email_from": self.env.user.id,
                            "email_to": each.lvl1_user_ids.name,
                            "recipient_ids": [(6,0, [each.lvl1_user_ids.partner_id.id])],
                            "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            }
                            if mail_dict:
                                mail_create = self.env['mail.mail'].create(mail_dict)
                                mail_create.send()
                            if self.env.user.id != current_id.create_uid.id:
                                mail_dict_1 = {
                                "subject": 'Purchase Order Reject',
                                "email_from": self.env.user.id,
                                "email_to": current_id.create_uid.name,
                                "recipient_ids": [(6,0, [current_id.create_uid.partner_id.id])],
                                "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                                }
                                if mail_dict_1:
                                    mail_create = self.env['mail.mail'].create(mail_dict_1)
                                    mail_create.send()
                            break
                        
                        else:
                            raise UserError (_("You can't reject the order"))
                            break

                    if each.approval_level == '3rdlvlapproval':
                        if (self.env.user.id in each.lvl1_user_ids.ids and  each.is_1st_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))
                            # mail_dict_2 = {
                            # "subject": 'Purchase Order Reject',
                            # "email_from": self.env.user.id,
                            # "email_to": each.lvl2_user_ids.name,
                            # "recipient_ids": [(6,0, [each.lvl2_user_ids.partner_id.id])],
                            # "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            # }
                            # if mail_dict_2:
                            #     mail_create_2 = self.env['mail.mail'].create(mail_dict_2)
                            #     mail_create_2.send()
                            # mail_dict_3 = {
                            # "subject": 'Purchase Order Reject',
                            # "email_from": self.env.user.id,
                            # "email_to": each.lvl3_user_ids.name,
                            # "recipient_ids": [(6,0, [each.lvl3_user_ids.partner_id.id])],
                            # "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            # }
                            # if mail_dict_3:
                            #     mail_create_3 = self.env['mail.mail'].create(mail_dict_3)
                            #     mail_create_3.send()
                            break

                        if (self.env.user.id in each.lvl2_user_ids.ids and  each.is_2nd_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))
                            mail_dict_2 = {
                            "subject": 'Purchase Order Reject',
                            "email_from": self.env.user.id,
                            "email_to": each.lvl1_user_ids.name,
                            "recipient_ids": [(6,0, [each.lvl1_user_ids.partner_id.id])],
                            "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            }
                            if mail_dict_2:
                                mail_create_2 = self.env['mail.mail'].create(mail_dict_2)
                                mail_create_2.send()
                            if self.env.user.id != current_id.create_uid.id:
                                mail_dict_1 = {
                                "subject": 'Purchase Order Reject',
                                "email_from": self.env.user.id,
                                "email_to": current_id.create_uid.name,
                                "recipient_ids": [(6,0, [current_id.create_uid.partner_id.id])],
                                "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                                }
                                if mail_dict_1:
                                    mail_create = self.env['mail.mail'].create(mail_dict_1)
                                    mail_create.send()
                            # mail_dict_3 = {
                            # "subject": 'Purchase Order Reject',
                            # "email_from": self.env.user.id,
                            # "email_to": each.lvl3_user_ids.name,
                            # "recipient_ids": [(6,0, [each.lvl3_user_ids.partner_id.id])],
                            # "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            # }
                            # if mail_dict_3:
                            #     mail_create_3 = self.env['mail.mail'].create(mail_dict_3)
                            #     mail_create_3.send()
                            break
                        if (self.env.user.id in each.lvl3_user_ids.ids and  each.is_3rd_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))
                            mail_dict_2 = {
                            "subject": 'Purchase Order Reject',
                            "email_from": self.env.user.id,
                            "email_to": each.lvl2_user_ids.name,
                            "recipient_ids": [(6,0, [each.lvl2_user_ids.partner_id.id])],
                            "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            }
                            if mail_dict_2:
                                mail_create_2 = self.env['mail.mail'].create(mail_dict_2)
                                mail_create_2.send()
                            mail_dict_3 = {
                            "subject": 'Purchase Order Reject',
                            "email_from": self.env.user.id,
                            "email_to": each.lvl1_user_ids.name,
                            "recipient_ids": [(6,0, [each.lvl1_user_ids.partner_id.id])],
                            "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                            }
                            if mail_dict_3:
                                mail_create_3 = self.env['mail.mail'].create(mail_dict_3)
                                mail_create_3.send()
                            if self.env.user.id != current_id.create_uid.id:
                                mail_dict_1 = {
                                "subject": 'Purchase Order Reject',
                                "email_from": self.env.user.id,
                                "email_to": current_id.create_uid.name,
                                "recipient_ids": [(6,0, [current_id.create_uid.partner_id.id])],
                                "body_html": "Hello This Purchase Order " + current_id.name + " Rejected."
                                }
                                if mail_dict_1:
                                    mail_create = self.env['mail.mail'].create(mail_dict_1)
                                    mail_create.send()
                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break
           
            