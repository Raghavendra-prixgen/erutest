from odoo import models, fields, api, _
from num2words import num2words


    
class DebitCreditNote(models.Model):
    _inherit = 'account.move'  
    
    def get_purchase_order(self,value):
        # res = self.env['account.move.line'].search([('product_id', '!=', False)], limit=1)
        res = self.env['purchase.order'].search([('name', '!=', self.invoice_origin)],limit=1)
        # val = res.mapped('purchase_line_id')
        print(res,"////////////////////////////////////////////////////////////")
        return res
    
    def get_round_off_value(self,invoice_id):
       
        
        return round(round(self.tax_totals['amount_total']) - (self.tax_totals['amount_total']),2)



    # def amount_words(self, amount):
    #     # amount1 = 100
    #     amount1 = str(amount)
    #     amt = amount1.split(',')
    #     if int(amt[0]) > 0:
    #         second_part = ' and ' + \
    #             num2words(int(amt[0]), lang='en_IN') + ' Rupees '
    #     else:
    #         second_part = ' Only '

    #     return ' Rupees ' + num2words(int(amt[0]), lang='en_IN') + ' Only '
    
    
    
    def get_taxes_debit_credit(self):
       
        tax_name =[]
        taxess = []
        taxes = []
        sorted_tax=[]
        for line in self.invoice_line_ids:
            curr_val = line.price_subtotal
            tot_rax_rate =0.0
            igst_val = 0.0

            sgst_rate =0.0
            sgst_val = 0.0

            cgst_rate = 0.0
            cgst_val =0.0

            tcs_rate =0.0
            tcs_val =0.0
            cess_val = 0.0
            group =''
            
            
            
            for each_tax in line.tax_ids:
                

                if each_tax:
                    tax_name.append(each_tax)


        
                    if each_tax.amount_type == 'group':
                       
                        if each_tax.tax_group_id.name == 'GST':
                            for each_group_line in  each_tax.children_tax_ids:
                                group  = each_tax.tax_group_id.name
                                if each_group_line.tax_group_id.name == 'SGST' or each_group_line.tax_group_id.name == 'CGST' :
                                    tot_rax_rate += round(each_group_line.amount,2)
                                    sgst_val =round(curr_val * (each_group_line.amount/100),2)
                                elif each_group_line.tax_group_id.name == 'TCS':
                                    tcs_rate = each_group_line.amount
                                    tcs_val = round((curr_val+sgst_val*2) * (each_group_line.amount/100),2)




                        
                        elif each_tax.tax_group_id.name == 'IGST':
                            
                            for each_group_line in  each_tax.children_tax_ids:
                                group = each_tax.tax_group_id.name
                                if each_group_line.tax_group_id.name != 'TCS':
                                    tot_rax_rate += round(each_tax.amount,2)
                                    
                                    
                                    igst_val =round(curr_val * (each_tax.amount/100),2)
                                elif each_group_line.tax_group_id.name == 'TCS':
                                    tcs_rate =  each_group_line.amount
                                    tcs_val = round((curr_val+igst_val) * (each_group_line.amount/100),2)



                    else:
                        
                        val = self.tax_totals
                        val_dict= val
                        for  value in val_dict.get('groups_by_subtotal').get('Untaxed Amount'):
                            if value.get('tax_group_name') == 'Cess':
                                cess_val = value.get('tax_group_amount')
                                

                        if each_tax.amount == 0.1000:
                            group = each_tax.tax_group_id.name
                        
                            # tot_rax_rate +=round(each_tax.amount)
                            tot_rax_rate +=each_tax.amount
                            
                            igst_val = round(curr_val * (each_tax.amount/100),2)
                            
                        else:
                            group = each_tax.tax_group_id.name
                            tot_rax_rate +=round(each_tax.amount)
                            
                            igst_val = round(curr_val * (each_tax.amount/100),2)
                            
                    

                    # taxes.append({'hsn':line.product_id.l10n_in_hsn_code,'tax':line.tax_ids,'tax_rate':tot_rax_rate,'igst':igst_val,'sgst':sgst_val,'tcs':tcs_val,'tcs_rate':tcs_rate, 'tax_group':group,'cess_val':cess_val})
                    taxess.append({'tax':line.tax_ids,'tax_rate':tot_rax_rate,'tcs':tcs_val,'tcs_rate':tcs_rate, 'tax_group':group,'cess_val':cess_val})


                


                    for each_tax_id in tax_name:
                        
                        tot_rax_rate =0.0
                        igst_val =0.0
                        sgst_val =0.0
                        tcs_val =0.0
                        tcs_rate =0.0
                        group =''

                        for each_rec in taxes:
                            print("iuytfjkuytf",each_rec['tax'])
                            print("wertyuilm",each_tax_id)


                            if each_tax_id.id == each_rec['tax']:
                                tot_rax_rate = each_rec['tax_rate']
                               
                                tcs_rate = each_rec['tcs_rate']
                                igst_val+=each_rec['igst']
                                sgst_val+=each_rec['sgst']
                                tcs_val+=each_rec['tcs']
                                group=each_rec['tax_group'] 
                            else:
                                # tot_rax_rate = each_rec['tax_rate']
                                # igst_val = each_rec['igst']line.tax_id
                                # sgst_val = each_rec['sgst']
                                # tcs_val = each_rec['tcs']
                                # group = each_rec['tax_group']
                                continue

                        sorted_tax.append({'tax':each_tax_id,'tax_rate':tot_rax_rate,'igst':igst_val,'sgst':sgst_val,'tcs':tcs_val,'tcs_rate':tcs_rate,'tax_group':group})
        
        


        # print(sorted_tax,1111111111111111111111111111111111111111111111111,taxess)
        
        result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in taxess)]
        
        result.reverse()

        tax_name = list(set(tax_name))
        print(result,8888888888888888888888888888888888888888888888888888888888888888888888888888888888)
        return result
    
    # def get_taxes(self):
    #     print(7777777777777777777777777777777777777777777777777777777777777777)
    #     tax_name =[]
    #     taxes = []
    #     price_sub = []
    #     sorted_tax=[]
    #     tot_rax_rate=0.0
    #     for line in self.invoice_line_ids:
    #         curr_val  =0.0
    #         igst_val = 0.0
    #         sgst_rate =0.0
    #         sgst_val = 0.0
			
    #         cgst_rate = 0.0
    #         cgst_val =0.0
            
    #         tcs_rate =0.0
    #         tcs_val =0.0
    #         cess_val = 0.0
    #         group =''
            
            
    #         for each_tax in line.tax_ids:
    #             if each_tax:
    #                 tax_name.append(each_tax)
                    
    #                 if each_tax.amount_type == 'group':
    #                     if each_tax.tax_group_id.name == 'GST':
    #                         for each_group_line in  each_tax.children_tax_ids:
    #                             group  = each_tax.tax_group_id.name
    #                             if each_group_line.tax_group_id.name == 'SGST' or each_group_line.tax_group_id.name == 'CGST' :
    #                                 tot_rax_rate +=round(each_group_line.amount,2)
    #                                 sgst_val=round(curr_val * (each_group_line.amount/100),2)
    #                             elif each_group_line.tax_group_id.name == 'TCS':
    #                                 tcs_rate = each_group_line.amount
    #                                 tcs_val = round((curr_val+sgst_val*2) * (each_group_line.amount/100),2)
                                    
                        
    #                     elif each_tax.tax_group_id.name == 'IGST':
    #                         for each_group_line in  each_tax.children_tax_ids:
    #                             group = each_tax.tax_group_id.name
    #                             if each_group_line.tax_group_id.name != 'TCS':
    #                                 tot_rax_rate += round(each_tax.amount,2)
    #                                 igst_val =round(curr_val * (each_tax.amount/100),2)
    #                             elif each_group_line.tax_group_id.name == 'TCS':
    #                                 tcs_rate =  each_group_line.amount
    #                                 tcs_val = round((curr_val+igst_val) * (each_group_line.amount/100),2)
                                    
    #                 else:
    #                     val_dict = self.tax_totals
    #                     # val_dict= json.loads(val)
    #                     for  value in val_dict.get('groups_by_subtotal').get('Untaxed Amount'):
    #                         if value.get('tax_group_name') == 'Cess':
    #                             cess_val = value.get('tax_group_amount')
                                
                                
    #                     group = each_tax.tax_group_id.name
    #                     tot_rax_rate +=round(each_tax.amount)
    #                     igst_val = round(curr_val * (each_tax.amount/100),2)
                    
    #                 taxes.append({'hsn':line.product_id.l10n_in_hsn_code,'tax':line.tax_ids,'tax_rate':tot_rax_rate,'igst':igst_val,'sgst':sgst_val,'tcs':tcs_val,'tcs_rate':tcs_rate,'price_sub':curr_val, 'tax_group':group,'cess_val':cess_val})
                    
                    
                    
                    
    #             for each_tax_id in tax_name:
    #                 tot_rax_rate =0.0
    #                 igst_val =0.0
    #                 sgst_val =0.0
    #                 tcs_val =0.0
    #                 tcs_rate =0.0
    #                 group =''
                    
    #                 for each_rec in taxes:
    #                     if each_tax_id.id == each_rec['tax'].ids:
    #                         tot_rax_rate = each_rec['tax_rate']
    #                         tcs_rate = each_rec['tcs_rate']
    #                         igst_val+=each_rec['igst']
    #                         sgst_val+=each_rec['sgst']
    #                         tcs_val+=each_rec['tcs']
    #                         group=each_rec['tax_group']
    #                     else:
    #                         # tot_rax_rate = each_rec['tax_rate']
    #                         # igst_val = each_rec['igst']
    #                         # sgst_val = each_rec['sgst']
    #                         # tcs_val = each_rec['tcs']
    #                         # group = each_rec['tax_group']
    #                         continue
                        
    #                 sorted_tax.append({'tax':each_tax_id,'tax_rate':tot_rax_rate,'igst':igst_val,'sgst':sgst_val,'tcs':tcs_val,'tcs_rate':tcs_rate,'tax_group':group})
    #                 # result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in sorted_tax)]
    #     result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in taxes)]
    #     result = sorted(result, key=lambda x: x['hsn'])
        
    #     tax_name = list(set(tax_name))
    #     print(result,8888888888888888888888888888888888888888888888888888888888888888888888888888888888)
        
    #     return result

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_product_packaging_id(self, sale_line_ids):
        sale_data = sale_line_ids.product_packaging_id.mapped('name')
        if sale_data:
            return ",".join(sale_data)
        else:
            return ''

    def get_product_packaging_qty(self, sale_line_ids):
        return round(sum(sale_line_ids.mapped('product_packaging_qty')))

    def get_boxes_invoice(self,line):
        stock_move = sum(line.stock_move_ref.move_ids_without_package.filtered(lambda x:x.product_id == line.product_id and line.quantity == x.quantity_done).mapped('z_done_qty_in_boxes'))
        if stock_move:
            return int(stock_move)

        else:
            return 0

    def get_boxes_del(self,line):
        boxes = sum(line.move_id.sto_out_picking_id.move_ids_without_package.filtered(lambda x:x.product_id == line.product_id).mapped('z_done_qty_in_boxes'))
        if boxes:
            return int(boxes)

        else:
            return 0

    def get_packaging_name(self,line):
        package_name = line.move_id.sto_id.sto_line_ids.filtered(lambda x:x.product_id == line.product_id).mapped('product_packaging_id.name')
        if package_name:
            return str(package_name)

        else:
            return ''




    











































