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

    remarks = fields.Char( string='Remaks', required=True)
    
   
    def reject_order(self):
        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)
        
        active_id =self.env.context['active_id']
        current_id=self.env['sale.order'].search([('id','=',active_id)])
        if current_id.sale_approval_line:

            for each in  current_id.sale_approval_line:
                if each.is_approve == False:
                    if current_id.approval_method == 'amount':
                        if (self.env.user.id in each.user_ids.ids and  each.is_approve == False ) and current_id.amount_total< each.amount :
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break
                    
                    elif current_id.approval_method == 'stages':
                        if (self.env.user.id in each.user_ids.ids and  each.is_approve == False ):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break

                    
        if current_id.sale_lvl_amt_approval_line:
            for each in  current_id.sale_lvl_amt_approval_line:
 
                approval_ids = self.env['sale.approval'].search([('document_type_id','=',current_id.doc_type_id.id)])

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

                            break

                        if (self.env.user.id in each.lvl2_user_ids.ids and  each.is_2nd_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))

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

                            break

                        if (self.env.user.id in each.lvl2_user_ids.ids and  each.is_2nd_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))

                            break
                        if (self.env.user.id in each.lvl3_user_ids.ids and  each.is_3rd_user_completed == False):
                            each.remarks = self.remarks
                            current_id.state = 'reject'
                            current_id.to_approve_states = 'reject'

                            current_id.message_post(body=_("Reject Reason %s ")% (self.remarks))

                            break
                        else:
                            raise UserError (_("You can't reject the order"))
                            break
           
            