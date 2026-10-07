from odoo import models, fields, api, _
from odoo.exceptions import UserError
from num2words import num2words

class CommercialInvoiceReport(models.Model):
    _inherit = ['account.move']



    def sale_order(self):
        joined_names = ','.join(self.invoice_line_ids.sale_line_ids.order_id.mapped('name'))
        return joined_names

    def sale_order_date(self):
        dates = []
        for sale_date in self.invoice_line_ids.sale_line_ids.order_id.mapped('date_order'):
            filter_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(sale_date))
            date_str = filter_date.strftime('%d-%m-%Y %H:%M:%S')
            dates.append(date_str)
        return ', '.join(dates)


    def sale_order_po_ref(self):
        po_refs = self.invoice_line_ids.mapped('sale_line_ids.order_id.y_po_ref')
        return ', '.join(ref for ref in po_refs if ref)
    

    def sale_order_po_date(self):
        dates = []
        for po_date in self.invoice_line_ids.mapped('sale_line_ids.order_id.y_po_date'):
            if po_date:
                filter_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(po_date))
                date_str = filter_date.strftime('%d-%m-%Y %H:%M:%S')
                dates.append(date_str)
        return ', '.join(dates) if dates else None

   

        
    
    def amount_in_words(self, amount):
        formatted_amount = "{:,.2f}".format(amount)
        amt = formatted_amount.split(".")
        amt[0] = amt[0].replace(",", "")  
    

        currency = self.currency_id.currency_unit_label


        if int(amt[1]) > 0:
            second_part = currency + '' + " and " + num2words(int(amt[1]), lang='en_IN') + ' Paise only'
            remove_and_new = second_part.replace('.', " and ")
            remove_and_pro = remove_and_new.replace('-', ' ')
        else:
            second_part = 'only'
        
        first_part =  num2words(int(amt[0]), lang='en_IN').replace(' and', ' ')
        first_part_new = first_part.replace(',', '')

        first_part_pro = first_part_new.replace('-', ' ')
        if int(amt[1]) == 0:
            result = first_part_pro + ' '+ currency +' ' + second_part
        else:
            result = first_part_pro + ' ' + remove_and_pro
        results = ' '.join(word.capitalize() for word in result.split())
        final_result = results.replace('And', " and ")

    
        return final_result
