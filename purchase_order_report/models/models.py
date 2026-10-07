from odoo import models, fields, api, _
from num2words import num2words


class PurchaseOrderReport(models.Model):
    _inherit = 'purchase.order'   


    def amount_in_words(self, amount):
        formatted_amount = "{:,.2f}".format(amount)
        amt = formatted_amount.split(".")
        amt[0] = amt[0].replace(",", "")  
    
        if int(amt[1]) > 0:
            second_part = "and " + num2words(int(amt[1]), lang='en_IN') + ' Paise only'
            remove_and_new = second_part.replace('.', " and ")
            remove_and_pro = remove_and_new.replace('-', ' ')
        else:
            second_part = 'only'
        currency = self.currency_id.currency_unit_label
        
        first_part = currency + ' ' + num2words(int(amt[0]), lang='en_IN').replace(' and', ' ')
        first_part_new = first_part.replace(',', '')
        first_part_pro = first_part_new.replace('-', ' ')
        if int(amt[1]) == 0:
            result = first_part_pro + ' ' + second_part
        else:
            result = first_part_pro + ' ' + remove_and_pro
        results = ' '.join(word.capitalize() for word in result.split())
        final_result = results.replace('And', " and ")

    
        return final_result

   

    def tax_calculation(self):
        taxes_list = []
        for line in self.order_line:
            for each_line in line.taxes_id:
                taxes_res=each_line.compute_all(
                    quantity=line.product_qty,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=self.partner_id,
                    price_unit=line.price_unit,
                    is_refund=False,
                    )
                taxes_res.update({'product_id':line.product_id.id,'line_id':line.id,'tax_group':line.taxes_id.description,'tax_name':each_line.name.split('%')[0]})
                taxes_list.append(taxes_res)
        return taxes_list
     

    
    



    











































