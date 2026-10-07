from datetime import date
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError,ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for rec in self:
            current_date = (datetime.now().date())
            if rec.date:            
                if rec.date > current_date:
                    raise UserError('Accounting date should not be grater than current date!')
        return super(AccountMove,self).action_post()     
    
