from odoo import models, fields, api, _, tools
from datetime import date
import datetime
from odoo.exceptions import ValidationError
from datetime import timedelta, date, datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    manager_sale_id = fields.Many2one('res.partner', string="Document Responsibility")    
    sale_doc_note_ids = fields.One2many('sale.document.notification', 'sale_order_id', string="Document name")
        
class DocumentsNotficationExpiry(models.Model):
    _name = 'sale.document.notification'    
    
    user_log_id = fields.Many2one('res.users', default=lambda self: self.env.user)   
    sale_order_id = fields.Many2one('sale.order', string='Name')    
    name = fields.Char('Document Name', tracking=True)
    sale_attachment_ids = fields.Many2many('ir.attachment', string='Attachments', tracking=True)
    order_notification = fields.Integer(string='Notification Days', tracking=True)
    sale_expiry_date = fields.Date(string='Expiry Date', tracking=True)
    sale_notify_day = fields.Boolean(string='Notify', tracking=True)
    sale_day_expiry =  fields.Integer(string="Remaining Days", compute="compute_get_days_sale", tracking=True)
    state = fields.Selection([('running','Running'),('notify','notified'),('expired','Expired')], 
        string="Status", default='running', tracking=True)
    today_date = fields.Date(string="Today's date", default=datetime.today())
    sale_today_date = fields.Date(string="Today's date", tracking=True)
    doc_value = fields.Char(string="doc_value", tracking=True)
    
    @api.depends('sale_today_date')
    def compute_get_days_sale(self):
        for val in self:
            val.sale_today_date = date.today()
            if val.sale_expiry_date and val.sale_today_date:
                t_val = val.sale_today_date
                e_val = val.sale_expiry_date
                tot_val = e_val - t_val
                if int(tot_val.days) <= 0:
                    val.sale_day_expiry = 0
                else:
                    val.sale_day_expiry = str(tot_val.days)

    def document_expiry_mail_send_sale(self):
        self = self.sudo()
        value = self.search([('state','=','running')])
        exp = self.search([('state','=','notify')])
        for line in value:
            line.sale_today_date = date.today()
            if line.sale_notify_day:
                if line.sale_expiry_date and line.order_notification != 0:
                    days_notify = line.sale_expiry_date - timedelta(line.order_notification)
                    if line.sale_today_date == days_notify:
                        if line.sale_order_id.manager_sale_id.email:
                            mail_template = self.env.ref('sale_document_notification.email_template_of_document_expiring_sale')                            
                            email_values = {
                            'email_to': line.sale_order_id.manager_sale_id.email,
                            'email_from': line.user_log_id.email,
                            'attachment_ids':[(6,0,line.sale_attachment_ids.ids)]
                            }
                            mail_template.send_mail(line.id,force_send=True,email_values = email_values)                        
                            line.state = 'notify'
        for list_in in exp:
            if list_in.sale_expiry_date == list_in.sale_today_date :
                list_in.state = 'expired'
