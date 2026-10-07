# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context
import datetime
from datetime import date
from datetime import datetime



class CancelReasonPurchaseOrder(models.Model):
    _name = 'in.cancel.reason'
    _rec_name = 'y_name'

    y_name = fields.Char( string="Cancel Discription")



class CancelReasonWizard(models.TransientModel):
    _name = 'in.cancel.reason.wizard.purchase'
    
    y_in_cancel_wizard_id = fields.Char(string="Reason for Cancel", size=50)
    
    def action_cancel_done(self):
        activities = []
        
        for rec in self:
            cancel_id = self.env['purchase.order'].browse(self.env.context.get('active_ids'))
            for cancel_id in cancel_id:
                cancel_id.button_cancel()
                cancel_id.picking_ids.action_cancel()
                cancel_id.write({
                    'y_cancel_reason_id': self.y_in_cancel_wizard_id,  
                    'state' : 'cancel'            
                })  