from odoo import models, fields, api, _
from num2words import num2words


class StockPicking(models.Model):
    _inherit = 'stock.picking'   

    def get_amount_total(self):
        total_taxable_amount = 0.0
        for line in self.move_line_ids:
            total_taxable_amount += line.quantity * line.product_id.standard_price
        return total_taxable_amount
    
    def get_rat_total(self):
        total_rate_amount = 0.0
        for rat_line in self.move_line_ids:
            total_rate_amount += rat_line.product_id.taxes_id.amount / 100
        return total_rate_amount

    def get_tax_amount_total(self):
        tax_line = 0.0
        for tax_amount_line in self.move_line_ids:
            tax_line += (tax_amount_line.quantity * tax_amount_line.product_id.standard_price) * (tax_amount_line.product_id.taxes_id.amount / 100)
        return tax_line

    def get_grand_total(self):
        grand_line = 0.0
        for total_line in self.move_line_ids:
            grand_line += (total_line.quantity * total_line.product_id.standard_price) + (total_line.quantity * total_line.product_id.standard_price) * (total_line.product_id.taxes_id.amount / 100)
        return grand_line

    def amount_in_words_sales(self):
        grand_line_words = self.get_grand_total()
        amount = "{:.2f}".format(grand_line_words)
        amount1 = str(amount)
        amt= amount1.split(".")
        if int(amt[1]) > 0:
            second_part = ' and '+ num2words(int(amt[1]), lang='en_IN') + ' Paise only '
        else:
            second_part = ' Only '

        return ' Rupees ' + num2words(int(amt[0]), lang='en_IN') + second_part 
    



    











































