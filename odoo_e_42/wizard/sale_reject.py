# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context
import datetime
from datetime import date
from datetime import datetime


class Saleremarks(models.TransientModel):
    _name = 'sale.approval.remarks'
    _description = 'sale.approval.remarks'

    y_remarks = fields.Char( string='Remaks', required=True)


    def reject_order_mail(self, each, current_id):
        each.y_remarks = self.y_remarks
        current_id.state = 'reject'
        current_id.y_to_approve_states = 'reject'
        current_id.message_post(body=_("Reject Reason: %s ") % (self.y_remarks))

    # def send_rejection_emails(self, each, current_id, user_lists):
    #     for user_list in user_lists:
    #         for user in user_list:
    #             mail_dict = {
    #                 "subject": 'Sale Order Reject',
    #                 "email_from": self.env.user.name,
    #                 "email_to": user.name,
    #                 "recipient_ids": [(6, 0, [user.partner_id.id])],
    #                 "body_html": f"Hello, This Sale Order {current_id.name} has been rejected."
    #             }
    #             if mail_dict:
    #                 mail_create = self.env['mail.mail'].create(mail_dict)
    #                 mail_create.send()
    
   
    
   
    def reject_order(self):
        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)
        
        active_id =self.env.context['active_id']
        current_id=self.env['sale.order'].search([('id','=',active_id)])
        if current_id.y_sale_approval_line:

            for each in  current_id.y_sale_approval_line:
                if each.y_is_approve == False:
                    if current_id.y_approval_method == 'amount':
                        if (self.env.user.id in each.y_user_ids.ids and  each.y_is_approve == False ) and current_id.amount_total< each.y_amount :
                            each.y_remarks = self.y_remarks
                            current_id.state = 'reject'
                            current_id.y_to_approve_states = 'reject'

                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break
                    
                    elif current_id.y_approval_method == 'stages':
                        if (self.env.user.id in each.y_user_ids.ids and  each.y_is_approve == False ):
                            each.y_remarks = self.y_remarks
                            current_id.state = 'reject'
                            current_id.y_to_approve_states = 'reject'

                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            

                    
        # if current_id.y_sale_lvl_amt_approval_line:
        #     for each in  current_id.y_sale_lvl_amt_approval_line:
 
        #         approval_ids = self.env['sale.approval'].search([('y_document_type_id','=',current_id.y_doc_type_id.id)])

        #         if approval_ids.y_approval_method == 'y_lvlsamt':
        #             if each.y_approval_level == '1stlvlapproval':

        #                 if (self.env.user.id in each.y_lvl1_user_ids.ids and  each.y_is_1st_user_completed == False):
        #                     each.y_remarks = self.y_remarks
        #                     current_id.state = 'reject'
        #                     current_id.y_to_approve_states = 'reject'

        #                     current_id.message_post(body=_("Reject Reason %s ")% (self.y_remarks))

        #                     break
        #                 else:
        #                     raise UserError (_("You can't reject the order"))
                            

        #             if each.y_approval_level == '2ndlvlapproval':
        #                 if (self.env.user.id in each.y_lvl1_user_ids.ids and  each.y_is_1st_user_completed == False):
        #                     each.y_remarks = self.y_remarks
        #                     current_id.state = 'reject'
        #                     current_id.y_to_approve_states = 'reject'

        #                     current_id.message_post(body=_("Reject Reason %s ")% (self.y_remarks))

        #                     break

        #                 if (self.env.user.id in each.y_lvl2_user_ids.ids and  each.y_is_2nd_user_completed == False):
        #                     each.y_remarks = self.y_remarks
        #                     current_id.state = 'reject'
        #                     current_id.y_to_approve_states = 'reject'

        #                     current_id.message_post(body=_("Reject Reason %s ")% (self.y_remarks))

        #                     break
                        
        #                 else:
        #                     raise UserError (_("You can't reject the order"))
                            

        #             if each.y_approval_level == '3rdlvlapproval':
        #                 if (self.env.user.id in each.y_lvl1_user_ids.ids and  each.y_is_1st_user_completed == False):
        #                     each.y_remarks = self.y_remarks
        #                     current_id.state = 'reject'
        #                     current_id.y_to_approve_states = 'reject'

        #                     current_id.message_post(body=_("Reject Reason %s ")% (self.y_remarks))

        #                     break

        #                 if (self.env.user.id in each.y_lvl2_user_ids.ids and  each.y_is_2nd_user_completed == False):
        #                     each.y_remarks = self.y_remarks
        #                     current_id.state = 'reject'
        #                     current_id.y_to_approve_states = 'reject'

        #                     current_id.message_post(body=_("Reject Reason %s ")% (self.y_remarks))

        #                     break
        #                 if (self.env.user.id in each.y_lvl3_user_ids.ids and  each.y_is_3rd_user_completed == False):
        #                     each.y_remarks = self.y_remarks
        #                     current_id.state = 'reject'
        #                     current_id.y_to_approve_states = 'reject'

        #                     current_id.message_post(body=_("Reject Reason %s ")% (self.y_remarks))

        #                     break
        #                 else:
        #                     raise UserError (_("You can't reject the order"))
                            
           
        if current_id.y_sale_lvl_amt_approval_line:
            for each in current_id.y_sale_lvl_amt_approval_line:
                approval_ids = self.env['sale.approval'].search([('y_document_type_id','=',current_id.y_doc_type_id.id)])
                if approval_ids.y_approval_method == 'lvlsamt':
                    print('11111111111111111111111111111111111')
                    if each.y_approval_level:
                        if each.y_approval_level == '1stlvlapproval':
                            # Check if the user is eligible to reject the order and has not already approved it
                            if self.env.user.id in each.y_lvl1_user_ids.ids and not each.y_is_1st_user_completed:
                                self.reject_order_mail(each, current_id)
                            
                        elif each.y_approval_level == '2ndlvlapproval':
                            # Check if the user is eligible to reject the order and has not already approved it
                            if self.env.user.id in each.y_lvl2_user_ids.ids and not each.y_is_2nd_user_completed:
                                self.reject_order_mail(each, current_id)
                                # Send rejection emails to 1st level approvers
                                # self.send_rejection_emails(each, current_id, [each.y_lvl1_user_ids])
                                
                            elif self.env.user.id in each.y_lvl1_user_ids.ids and each.y_is_1st_user_completed:
                                raise UserError(_("You have already approved this order and cannot reject it now"))
                        elif each.y_approval_level == '3rdlvlapproval':
                            # Check if the user is eligible to reject the order and has not already approved it
                            if self.env.user.id in each.y_lvl3_user_ids.ids and not each.y_is_3rd_user_completed:
                                self.reject_order_mail(each, current_id)
                                # Send rejection emails to 2nd and 1st level approvers
                                # self.send_rejection_emails(each, current_id, [each.y_lvl2_user_ids, each.y_lvl1_user_ids])
                                
                            elif self.env.user.id in each.y_lvl2_user_ids.ids and each.y_is_2nd_user_completed:
                                raise UserError(_("You have already approved this order and cannot reject it now"))
                        else:
                            raise UserError(_("You can't reject the order at this level"))
