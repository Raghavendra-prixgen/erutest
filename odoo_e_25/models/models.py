from odoo import models, fields, api, _
from num2words import num2words


class ProformaInvoice(models.Model):
    _inherit = 'sale.order'   


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
    
        first_part = 'Rupees ' + num2words(int(amt[0]), lang='en_IN').replace(' and', ' ')
        first_part_new = first_part.replace(',', '')
        first_part_pro = first_part_new.replace('-', ' ')
        if int(amt[1]) == 0:
            result = first_part_pro + ' ' + second_part
        else:
            result = first_part_pro + ' ' + remove_and_pro
        results = ' '.join(word.capitalize() for word in result.split())
        final_result = results.replace('And', " and ")
        
        return final_result
    
    amount_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")


    @api.depends('amount_untaxed')
    def _compute_amount_total_words(self):
        for rec in self:
            rec.amount_words = rec.currency_id.amount_to_text(rec.amount_untaxed)

    
    
    

    # def function_for_bank_details_account_name_export(self):
    #     company = self.company_id.country_id
    #     sale = self.partner_id.country_id
    #     if company != sale:
    #         bank_details_export = self.company_id.parent_id.partner_id.bank_ids[0].filtered(lambda r: r.bank_id.export_bool)
    #         account_name_export = ', '.join([rec.bank_id.name for rec in bank_details_export])
    #         # print(account_name_export,"export name -----------------------------1")
    #         return account_name_export
    
    # def function_for_bank_details_account_numbers_export(self):
    #     company = self.company_id.country_id
    #     sale = self.partner_id.country_id
    #     if company != sale:
    #         bank_details_export = self.company_id.parent_id.partner_id.bank_ids[0].filtered(lambda r: r.bank_id.export_bool)
    #         account_numbers_export = ', '.join([rec.acc_number for rec in bank_details_export])
    #         # print(account_numbers_export,"export name -----------------------------1")
    #         return account_numbers_export
    
    
    # def function_for_bank_details_account_swift_code_export(self):
    #     company = self.company_id.country_id
    #     sale = self.partner_id.country_id
    #     if company != sale:
    #         bank_details_export = self.company_id.parent_id.partner_id.bank_ids[0].filtered(lambda r: r.bank_id.export_bool)
    #         account_swift_code_export = ', '.join([rec.bank_id.bic for rec in bank_details_export])
    #         # print(account_swift_code_export,"export name -----------------------------1")
    #         return account_swift_code_export
    
    # # ---------------------------------------------------------------------------
    
    # def function_for_bank_details_account_name_domestic(self):
    #     company = self.company_id.country_id
    #     sale = self.partner_id.country_id
    #     if company == sale:
    #         bank_details_domastic = self.company_id.parent_id.partner_id.bank_ids[0].filtered(lambda r: r.bank_id.domastic_bool)
    #         account_name_domastic = ', '.join([rec.bank_id.name for rec in bank_details_domastic])
    #         # print(account_name_domastic,"Domastic name -----------------------------1",bank_details_domastic)
    #         return account_name_domastic
    
    # def function_for_bank_details_account_numbers_domestic(self):
    #     company = self.company_id.country_id
    #     sale = self.partner_id.country_id
    #     if company == sale:
    #         bank_details_domastic = self.company_id.parent_id.partner_id.bank_ids[0].filtered(lambda r: r.bank_id.domastic_bool)
    #         account_numbers_domastic = ', '.join([rec.acc_number for rec in bank_details_domastic])
    #         # print(account_numbers_domastic,"Domastic number -----------------------------1",bank_details_domastic)
    #         return account_numbers_domastic
    
    
    # def function_for_bank_details_account_swift_code_domestic(self):
    #     company = self.company_id.country_id
    #     sale = self.partner_id.country_id
    #     if company == sale:
    #         bank_details_domastic = self.company_id.parent_id.partner_id.bank_ids[0].filtered(lambda r: r.bank_id.domastic_bool)
    #         account_swift_code_domastic = ', '.join([rec.bank_id.bic for rec in bank_details_domastic])
    #         # print(account_swift_code_domastic,"Domastic IFC -----------------------------1",bank_details_domastic)
    #         return account_swift_code_domastic
    
    

    











































