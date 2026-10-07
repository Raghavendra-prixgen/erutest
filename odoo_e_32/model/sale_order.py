from odoo import models, fields, api, _, tools
from datetime import date
import datetime
from odoo.exceptions import ValidationError
from datetime import timedelta, date, datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    y_manager_sale_id = fields.Many2one('res.partner', string="Document Responsibility")    
    # sale_doc_note_ids = fields.One2many('sale.document.notification', 'sale_order_id', string="Document name")
    y_cus_related_sale_doc_ids = fields.Many2many('sale.document.notification',string="Sale Documents") 
    y_customer_sale_doc_note_ids = fields.Many2many('sale.document.notification','sale_docs',string="Sale Documents") 

    @api.onchange('partner_id')
    def get_customer_doc_ids(self):
        for rec in self:
            if rec.partner_id:
                list_obj = rec.partner_id.y_sale_doc_note_ids.ids
                rec.y_cus_related_sale_doc_ids = list_obj
            else:
                rec.y_cus_related_sale_doc_ids = False
                   

    # def update_res(self):
    #     for rec in self:
    #         for record in rec.y_customer_sale_doc_note_ids:
    #             if record.y_sale_attachment_ids:
    #                 ir_att = self.env['ir.attachment'].browse(record.y_sale_attachment_ids.ids)
    #                 [att.write({'res_model':'sale.document.notification','res_id': record.id}) for att in ir_att]
        
class DocumentsNotficationExpiry(models.Model):
    _name = 'sale.document.notification'    
    
    y_user_log_id = fields.Many2one('res.users', default=lambda self: self.env.user)   
    y_sale_order_id = fields.Many2one('sale.order', string='Name')    
    y_name = fields.Char('Document Name', tracking=True)
    y_sale_attachment_ids = fields.Many2many('ir.attachment', string='Attachments', tracking=True)
    y_order_notification = fields.Integer(string='Notification Days', tracking=True)
    y_sale_expiry_date = fields.Date(string='Expiry Date', tracking=True)
    y_sale_notify_day = fields.Boolean(string='Notify', tracking=True)
    y_sale_day_expiry =  fields.Integer(string="Remaining Days", compute="compute_get_days_sale", tracking=True)
    y_state = fields.Selection([('running','Running'),('notify','notified'),('expired','Expired')], 
        string="Status", default='running', tracking=True)
    y_today_date = fields.Date(string="Today's date", default=datetime.today())
    y_sale_today_date = fields.Date(string="Today's date", tracking=True)
    y_doc_value = fields.Char(string="doc_value", tracking=True)
    y_customer_doc_id = fields.Many2one('res.partner', string="Customer")
    
    def create(self,values):
        res = super(DocumentsNotficationExpiry, self).create(values)
        if res.y_sale_attachment_ids:
            ir_att = self.env['ir.attachment'].browse(res.y_sale_attachment_ids.ids)
            [att.write({'res_model':'sale.document.notification','res_id': res.id}) for att in ir_att]
        return res
    
    
    @api.depends('y_sale_today_date')
    def compute_get_days_sale(self):
        for val in self:
            val.y_sale_today_date = date.today()
            if val.y_sale_expiry_date and val.y_sale_today_date:
                t_val = val.y_sale_today_date
                e_val = val.y_sale_expiry_date
                tot_val = e_val - t_val
                if int(tot_val.days) <= 0:
                    val.y_sale_day_expiry = 0
                else:
                    val.y_sale_day_expiry = str(tot_val.days)
            else:
                    val.y_sale_day_expiry = False

    def document_expiry_mail_send_sale(self):
        self = self.sudo()
        value = self.search([('y_state','=','running')])
        exp = self.search([('y_state','=','notify')])
        for line in value:
            line.y_sale_today_date = date.today()
            if line.y_sale_notify_day:
                if line.y_sale_expiry_date and line.y_order_notification != 0:
                    days_notify = line.y_sale_expiry_date - timedelta(line.y_order_notification)
                    if line.y_sale_today_date == days_notify:
                        if line.y_sale_order_id.y_manager_sale_id.email:
                            mail_template = self.env.ref('odoo_e_32.email_template_of_document_expiring_sale')                            
                            email_values = {
                            'email_to': line.y_sale_order_id.y_manager_sale_id.email,
                            'email_from': line.y_user_log_id.email,
                            'attachment_ids':[(6,0,line.y_sale_attachment_ids.ids)],
                            }
                            mail_template.send_mail(line.id,force_send=True,email_values = email_values)                        
                            line.y_state = 'notify'
        for list_in in exp:
            if list_in.y_sale_expiry_date == list_in.y_sale_today_date :
                list_in.y_state = 'expired'



class ResSaleDcumentation(models.Model):
    _inherit = 'res.partner'

    y_sale_doc_note_ids = fields.One2many('sale.document.notification', 'y_customer_doc_id', string="Document name")



class AttachmentCs(models.Model):
    _inherit = 'ir.attachment'
    
    @api.model
    def create(self, values):
        res = super(AttachmentCs, self).create(values)
        
        if isinstance(values, dict) and values.get('res_model') == 'sale.document.notification':
            res.write({'res_id': values.get('res_id')})
        
        return res