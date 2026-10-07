from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class PurchaseRegisterReportWizard(models.TransientModel):
    _name = "purchase.register.wizard"
    _description = ""

    y_date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    y_date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    y_choose_from = fields.Selection([       
        ('partner_id','Vendor'),
        ('categ_id','Product Category'),
        ])
    y_report_date = fields.Selection([('accounting','Accounting Date'),('invoice','Invoice Date')],default='accounting',string="Report On")
    y_categ_id = fields.Many2many('product.category', string="Product Category")
    y_partner_id = fields.Many2many('res.partner', string="Vendor")
   
    # Calling report method
    def retrieve_purchase_register(self):
        arg_list = []
        if self.y_report_date == 'accounting':
            date_clause = "AND move.date >= '{}' AND move.date <= '{}'".format(self.y_date_start,self.y_date_end)
        if self.y_report_date == 'invoice':
            date_clause = "AND move.invoice_date >= '{}' AND move.invoice_date <= '{}'".format(self.y_date_start,self.y_date_end)
        if self.y_choose_from:
            if self.y_partner_id and self.y_choose_from == 'partner_id':
                if len(self.y_partner_id.ids) > 1:
                    domain_clause = "AND move.partner_id in {}".format(tuple(self.y_partner_id.ids))
                else:
                    domain_clause = "AND move.partner_id = {}".format(self.y_partner_id.ids[0])
                date_clause+=domain_clause
            if self.y_categ_id and self.y_choose_from == 'categ_id':
                if len(self.y_categ_id.ids) > 1:
                    domain_clause = "AND pro_categ.id in {}".format(tuple(self.y_categ_id.ids))
                else:
                    domain_clause = "AND pro_categ.id = {}".format(self.y_categ_id.ids[0])
                date_clause+=domain_clause
        return self.env['purchase.register.report'].purchase_register_query(date_clause)
        
    @api.constrains('y_date_start')
    def _code_constrains(self):
        if self.y_date_start > self.y_date_end:
            raise ValidationError(_("'Start Date' must be before 'End Date'"))
