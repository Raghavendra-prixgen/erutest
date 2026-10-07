from odoo import models, fields, api, _
from num2words import num2words

class AccountMoveCustomReport(models.Model):
	_inherit = 'account.move'  


	
	def fetch_sale_order(self):
		sale_order_ids = self.invoice_line_ids[0].sale_line_ids.order_id.id
		sale_id = self.env["sale.order"].browse(sale_order_ids)
		return sale_id

	def amount_in_words_acc_move(self):
		amount = "{:.2f}".format(self.amount_residual)
		amount1 = str(amount)
		amt= amount1.split(".")
		if int(amt[1]) > 0:
			second_part = ' and '+ num2words(int(amt[1]), lang='en_IN') + ' Paise only '
			remove_and_new = second_part.replace('.', " and ")
			remove_and_pro = remove_and_new.replace('-', ' ')
		else:
			second_part = ' Only '

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
	
































