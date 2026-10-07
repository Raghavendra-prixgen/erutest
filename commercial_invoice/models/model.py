from odoo import models, fields, api, _

import num2words

class CommercialInvoiceReport(models.Model):
    _inherit = ['account.move']


    def sale_order(self):
        var = self.env['sale.order'].search([('name','=',self.invoice_origin)],limit=1)
        return var
