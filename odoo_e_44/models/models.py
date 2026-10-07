from odoo import models, fields, api,_

class MailTemplateCustomization(models.Model):
    _inherit = "mail.template"

    def _generate_template_attachments(self, res_ids, render_fields,render_results=None):
        
        if self.model_id.model == 'purchase.order':
            search_id_po = self.env['purchase.order'].search([('id','in',res_ids)])
            if search_id_po.state != 'draft':
                if search_id_po.partner_id.country_id  == search_id_po.company_id.country_id:
                    custom_report = self.env['ir.actions.report'].search([('name','=','Domestic Purchase Order')])
                    self.report_template_ids = custom_report
                elif search_id_po.partner_id.country_id  != search_id_po.company_id.country_id:
                    custom_report = self.env['ir.actions.report'].search([('name','=','Import Purchase Order')])
                    self.report_template_ids = custom_report
                else:
                    custom_report = self.env['ir.actions.report'].search([('name','=','Purchase Order')])
                    self.report_template_ids = custom_report
            else:
                custom_report = self.env['ir.actions.report'].search([('name','=','Request for Quotation')])
                self.report_template_ids = custom_report
                
        elif self.model_id.model == 'sale.order':  
            search_id_po = self.env['sale.order'].search([('id','in',res_ids)])
            if search_id_po.state != 'draft':
                if search_id_po.partner_id.country_id  == search_id_po.company_id.country_id:
                    custom_report = self.env['ir.actions.report'].search([('name','=','Domestic Proforma Invoice')])
                    self.report_template_ids = custom_report
                elif search_id_po.partner_id.country_id  != search_id_po.company_id.country_id:
                    custom_report = self.env['ir.actions.report'].search([('name','=','Export Proforma Invoice')])
                    self.report_template_ids = custom_report
            else:   
                custom_report = self.env['ir.actions.report'].search([('name','=','PDF Quote')])
                self.report_template_ids = custom_report
        render_results = super(MailTemplateCustomization,self)._generate_template_attachments(res_ids = res_ids, render_fields = render_fields,render_results=render_results)  
        return render_results
    
    
    