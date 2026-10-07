from odoo import models, fields, api, _
from num2words import num2words

class AccountMoveCustomReport(models.Model):
	_inherit = 'account.move'  

	def fetch_sale_order(self):
		sale_order_ids = self.invoice_line_ids[0].sale_line_ids.order_id.id
		sale_id = self.env["sale.order"].browse(sale_order_ids)
		return sale_id
      

	def tax_calculation(self):
		taxes_dict = {}
		for line in self.invoice_line_ids:
			line_taxes = {}
			for each_line in line.tax_ids:
				taxes_res = each_line.compute_all(
					quantity=line.quantity,
					currency=line.currency_id,
					product=line.product_id,
					partner=self.partner_id,
					price_unit=line.price_unit,
					is_refund=False,
				)
				for tax in taxes_res['taxes']:
					parent_tax = each_line.name
					tax_info = {
						'name': tax['name'],
						'amount': tax['amount'],
					}
					if parent_tax in line_taxes:
						# If the parent tax already exists, add the amount
						line_taxes[parent_tax]['amount'] += tax_info['amount']
					else:
						# Otherwise, initialize the parent tax entry
						line_taxes[parent_tax] = tax_info

			# Sum the amounts of different parent taxes
			total_tax_amount = sum([tax_info['amount'] for tax_info in line_taxes.values()])

			# Store both the total amount and the tax names for reference
			taxes_list = [{'name': k, 'amount': v['amount']} for k, v in line_taxes.items()]
			taxes_dict[line.id] = {'total_amount': total_tax_amount, 'taxes': taxes_list}

		return taxes_dict

	def amount_in_words_acc_move(self):
		amount = "{:.2f}".format(self.amount_total_signed)
		print(amount,'1111111111111111111111')
		amount1 = str(amount)
		amt= amount1.split(".")
		if int(amt[1]) > 0:
			second_part = ' and '+ num2words(int(amt[1]), lang='en_IN') + ' Paise only '
			remove_and_new = second_part.replace('.', " and ")
			remove_and_pro = remove_and_new.replace('-', ' ')
			amount_in_word = num2words(int(amt[0]), lang='en_IN') + ' Rupees ' + remove_and_pro
		else:
			amount_in_word = num2words(int(amt[0]), lang='en_IN') + ' Rupees Only'

		# Capitalize the first letter
		amount_in_words = ' '.join(word.capitalize() for word in amount_in_word.split())
		final_result = amount_in_words.replace('And', " and ")
		return final_result
		

		# currency = self.currency_id.currency_unit_label

		# first_part = currency + ' ' + num2words(int(amt[0]), lang='en_IN').replace(' and', ' ')
		# first_part_new = first_part.replace(',', '')
		# first_part_pro = first_part_new.replace('-', ' ')
		# if int(amt[1]) == 0:
		# 	result = first_part_pro + ' ' + second_part
		# else:
		# 	result = first_part_pro + ' ' + remove_and_pro
		# results = ' '.join(word.capitalize() for word in result.split())
		# final_result = results.replace('And', " and ")
		# return final_result

	





























