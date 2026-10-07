from odoo import models, fields, api, _
from num2words import num2words

class AccountMoveCustomReport(models.Model):
	_inherit = 'account.move'  

	def fetch_sale_order(self):
		sale_order_ids = self.invoice_line_ids[0].sale_line_ids.order_id.id
		sale_id = self.env["sale.order"].browse(sale_order_ids)
		return sale_id
      

	def tax_calculation(self):
		taxes_list = []
		for line in self.invoice_line_ids:
			for each_line in line.tax_ids:
				taxes_res=each_line.compute_all(
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=self.partner_id,
                    price_unit=line.price_unit,
                    is_refund=False,
                    )
				taxes_res.update({'product_id':line.product_id.id,'line_id':line.id,'tax_group':line.tax_ids.description})
				taxes_list.append(taxes_res)
				
		return taxes_list

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

	def get_total_tax(self):
		total_tax = 0.0
		for record in self.invoice_line_ids:
			total_tax += record.tax_ids.amount / 100
		return total_tax

	def get_total_tax_value(self):
		total_tax_value = 0.0
		for line in self.invoice_line_ids:
			total_tax_value += (line.quantity * line.price_unit) * line.tax_ids.amount / 100
		return total_tax_value

	def get_grand_amount(self):
		grand_value = 0.0
		for line in self.invoice_line_ids:
			grand_value += (line.quantity * line.price_unit) + (line.quantity * line.price_unit) * line.tax_ids.amount / 100
		return grand_value





























