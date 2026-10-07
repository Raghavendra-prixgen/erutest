from odoo import models, fields, api, _
from datetime import datetime, timedelta,date
import calendar
from xlwt import easyxf
import xlwt
import io
import base64
from odoo.exceptions import UserError, ValidationError
import datetime
import math
import pdb
from odoo.tools.misc import file_path, xlsxwriter
import json

class DistributorInvoiceReportWizard(models.TransientModel):
    _name = "invoice.reconciliation.report.wizard"
    _description = " "
        
    y_start_date = fields.Date(string="Start Date")
    y_end_date = fields.Date(string="End Date")
    y_project_report = fields.Binary('Report')
    y_file_name = fields.Char('File Name')
    y_project_report_printed = fields.Boolean('Invoice Report Printed')
    y_choose_on = fields.Selection([('customer','Customer'),('vendor','Vendor')],requred=True,default='vendor')
    
    @api.constrains('y_start_date','y_end_date')
    def _check_dates(self):
        for rec in self:
            if rec.y_end_date < rec.y_start_date:
                raise ValidationError(_("""End Date Can not be less than Start Date"""))

    def get_invoice_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Invoice Report')

        amount_tot = 0.0
        column_heading_style = workbook.add_format({'bold': True, 'align': 'center'})
        left_alignment = workbook.add_format({'align': 'left'})
        center_alignment = workbook.add_format({'align': 'center'})
        worksheet.freeze_panes(1, 0)

        worksheet.write(0, 0, "Customer",column_heading_style)
        worksheet.write(0, 1, "Invoice",column_heading_style)
        worksheet.write(0, 2, "Invoice Date",column_heading_style)
        worksheet.write(0, 3, "Due Date",column_heading_style)
        worksheet.write(0, 4, "Invoice Amount",column_heading_style)
        worksheet.write(0, 5, "Analytic Account",column_heading_style)
        worksheet.write(0, 6, "Payment Number",column_heading_style)
        worksheet.write(0, 7, "Payment Date",column_heading_style)
        worksheet.write(0, 8, "Payment Amount",column_heading_style)
        
        row = 1
        domain = [('invoice_date','>=',self.y_start_date),('invoice_date','<=',self.y_end_date),('payment_state','in',('in_payment','paid','partial')),('state','=','posted'),('move_type','in',('out_invoice','in_invoice'))]
        if self.y_choose_on == 'customer':
            domain+= [('move_type','=','out_invoice')]
        else:
            domain+= [('move_type','=','in_invoice')]
            worksheet.write(0, 0, "Unique Reference No",column_heading_style)
            worksheet.write(0, 1, "Debit Ac No",column_heading_style)
            worksheet.write(0, 2, "Beneficiary Ac No",column_heading_style)
            worksheet.write(0, 3, "Beneficiary Name",column_heading_style)
            worksheet.write(0, 4, "Amount",column_heading_style)
            worksheet.write(0, 5, "Pay Mode",column_heading_style)
            worksheet.write(0, 6, "Date",column_heading_style)
            worksheet.write(0, 7, "IFSC",column_heading_style)
            worksheet.write(0, 8, "Payable Location name",column_heading_style)
            worksheet.write(0, 9, "Print Location",column_heading_style)
            worksheet.write(0, 10, "Bene Mobile no",column_heading_style)
            worksheet.write(0, 11, "Bene email id",column_heading_style)
            worksheet.write(0, 12, "Ben add1",column_heading_style)
            worksheet.write(0, 13, "Ben add2",column_heading_style)
            worksheet.write(0, 14, "Ben add3",column_heading_style)
            worksheet.write(0, 15, "Ben add4",column_heading_style)
            worksheet.write(0, 16, "Description",column_heading_style)
            worksheet.write(0, 17, "PO Number",column_heading_style)
            worksheet.write(0, 18, "Add details 3",column_heading_style)
            worksheet.write(0, 19, "Add details 4",column_heading_style)
            worksheet.write(0, 20, "Add details 5",column_heading_style)
            worksheet.write(0, 21, "Invoice Number",column_heading_style)

            


            
            

        format2 = workbook.add_format({'num_format': 'dd/mm/yyyy','align': 'left'})

        account_move_ids = self.env['account.move'].search(domain)
        invoice_ids = []

        for move in account_move_ids:
            worksheet.write(row, 0,'',left_alignment)
            worksheet.write(row, 1,'',left_alignment)
            if move.partner_bank_id.acc_number:
                worksheet.write(row, 2,move.partner_bank_id.acc_number,center_alignment)
            else:
                worksheet.write(row, 2,'',center_alignment)

            if move.partner_bank_id.acc_holder_name:

                worksheet.write(row, 3,move.partner_bank_id.acc_holder_name,center_alignment)
            else:
                worksheet.write(row, 3,'',center_alignment)

            if move.id not in invoice_ids:
                invoice_ids.append(move.id)
                worksheet.write(row, 4,move.amount_total,center_alignment)
            else:
                worksheet.write(row, 4,'',left_alignment)


            worksheet.write(row, 5,'N',center_alignment)

            worksheet.write(row, 6,move.date,format2)


            if move.partner_bank_id.bank_id.bic:

                worksheet.write(row, 7,move.partner_bank_id.bank_id.bic,center_alignment)

            else:
                worksheet.write(row, 7,'',center_alignment)

            worksheet.write(row, 8,'',left_alignment)
            worksheet.write(row, 9,'',left_alignment)
            worksheet.write(row, 10,'',left_alignment)
            worksheet.write(row, 11,'',left_alignment)
            worksheet.write(row, 12,'',left_alignment)
            worksheet.write(row, 13,'',left_alignment)
            worksheet.write(row, 14,'',left_alignment)
            worksheet.write(row, 15,'',left_alignment)
            worksheet.write(row, 16,'',left_alignment)
            worksheet.write(row, 17,'',left_alignment)
            worksheet.write(row, 18,'',left_alignment)
            worksheet.write(row, 19,'',left_alignment)
            worksheet.write(row, 20,'',left_alignment)
            worksheet.write(row, 21,move.name,left_alignment)



            row += 1










        # if self.y_choose_on == 'customer':
        #     account_move_ids = self.env['account.move'].search(domain)
        #     invoice_ids = []
        #     for move in account_move_ids:
        #         check_payment = False
        #         partner_id = move.partner_id
        #         if move.invoice_payments_widget:
        #                 payment_dict = json.dumps(move.invoice_payments_widget,  indent=4, sort_keys=True, default=str)
        #                 varx = json.loads(payment_dict)
        #                 if varx and varx.get('content'):
        #                     for dict_values in varx.get('content'):
        #                         if dict_values.get('account_payment_id'):
        #                             payment_id = move.env['account.payment'].search([('id','=',dict_values.get('account_payment_id'))])
        #                             if payment_id:
        #                                 check_payment = True
        #                                 worksheet.write(row, 0,move.partner_id.name,left_alignment)
        #                                 worksheet.write(row, 1,move.name,left_alignment)
        #                                 worksheet.write(row, 2,move.invoice_date,format2)
        #                                 worksheet.write(row, 3,move.invoice_date_due,format2)
        #                                 if move.id not in invoice_ids:
        #                                     invoice_ids.append(move.id)
        #                                     worksheet.write(row, 4,move.amount_total,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 4,'',left_alignment)
                                        
        #                                 analytic_list = []
        #                                 analytic_distribution = ''
        #                                 if payment_id.analytic_distribution:
        #                                     for analytic in payment_id.analytic_distribution:
        #                                         analytic_list.append(int(analytic))
        #                                     analytic_distribution = payment_id.env['account.analytic.account'].search([('id','in',analytic_list)]).mapped('name')
        #                                     if analytic_distribution:
        #                                         analytic_distribution = ','.join(analytic_distribution)
                            
        #                                 worksheet.write(row, 5,analytic_distribution,left_alignment)
        #                                 worksheet.write(row, 6,payment_id.name,left_alignment)
        #                                 worksheet.write(row, 7,payment_id.date,format2)
        #                                 worksheet.write(row, 8,dict_values.get('amount'),center_alignment)
        #                                 worksheet.write(row, 9,(payment_id.date - move.invoice_date),center_alignment)
        #                                 if move.partner_bank_id.acc_number:
        #                                     worksheet.write(row, 10,move.partner_bank_id.acc_number,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 10,'',center_alignment)

        #                                 if move.partner_bank_id.acc_holder_name:

        #                                     worksheet.write(row, 11,move.partner_bank_id.acc_holder_name,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 11,'',center_alignment)

        #                                 worksheet.write(row, 12,'N',center_alignment)

        #                                 if move.partner_bank_id.bank_id.bic:

        #                                     worksheet.write(row, 13,move.partner_bank_id.bank_id.bic,center_alignment)

        #                                 else:
        #                                     worksheet.write(row, 13,'',center_alignment)
                                        
                                       

        #                                 row += 1

        #                         elif dict_values.get('move_id'):
        #                             move_id = move.env['account.move'].search([('move_type','=','entry'),('id','=',dict_values.get('move_id'))])
        #                             if move_id:
        #                                 check_payment = True
        #                                 worksheet.write(row, 0,move.partner_id.name,left_alignment)
        #                                 worksheet.write(row, 1,move.name,left_alignment)
        #                                 worksheet.write(row, 2,move.invoice_date,format2)
        #                                 worksheet.write(row, 3,move.invoice_date_due,format2)
        #                                 if move.id not in invoice_ids:
        #                                     invoice_ids.append(move.id)
        #                                     worksheet.write(row, 4,move.amount_total,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 4,'',left_alignment)
                                        
                                        
        #                                 purchase_order = ",".join(move.invoice_line_ids.purchase_line_id.order_id.mapped('name'))
        #                                 worksheet.write(row, 5,purchase_order,left_alignment)
        #                                 analytic_list = []
        #                                 analytic_distribution = ''
        #                                 analytic_line_ids = move_id.line_ids.filtered(lambda x:x.analytic_distribution).mapped('analytic_distribution')
        #                                 if analytic_line_ids:
        #                                     for analytic_dict in analytic_line_ids:
        #                                         for analytic in analytic_dict:
        #                                             analytic_list.append(int(analytic))
        #                                     analytic_distribution = move_id.env['account.analytic.account'].search([('id','in',analytic_list)]).mapped('name')
        #                                     if analytic_distribution:
        #                                         analytic_distribution = ','.join(analytic_distribution)
                            
        #                                 worksheet.write(row, 6,analytic_distribution,left_alignment)
        #                                 worksheet.write(row, 7,move_id.name,left_alignment)
        #                                 worksheet.write(row, 8,move_id.date,format2)
        #                                 worksheet.write(row, 9,dict_values.get('amount'),center_alignment)
        #                                 if move.partner_bank_id.acc_number:
        #                                     worksheet.write(row, 10,move.partner_bank_id.acc_number,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 10,'',center_alignment)

        #                                 if move.partner_bank_id.acc_holder_name:

        #                                     worksheet.write(row, 11,move.partner_bank_id.acc_holder_name,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 11,'',center_alignment)

        #                                 worksheet.write(row, 12,'N',center_alignment)

        #                                 if move.partner_bank_id.bank_id.bic:

        #                                     worksheet.write(row, 13,move.partner_bank_id.bank_id.bic,center_alignment)

        #                                 else:
        #                                     worksheet.write(row, 13,'',center_alignment)


        #                                 row += 1



                
        #         if check_payment:
        #             row += 1
        # else:
        #     account_move_ids = self.env['account.move'].search(domain).invoice_line_ids.filtered(lambda x:x.purchase_line_id).mapped('move_id')
        #     invoice_ids = []
        #     for move in account_move_ids:
        #         check_payment = False
        #         partner_id = move.partner_id
        #         if move.invoice_payments_widget:
        #                 payment_dict = json.dumps(move.invoice_payments_widget,  indent=4, sort_keys=True, default=str)
        #                 varx = json.loads(payment_dict)
        #                 if varx and varx.get('content'):
        #                     for dict_values in varx.get('content'):
        #                         if dict_values.get('account_payment_id'):
        #                             payment_id = move.env['account.payment'].search([('id','=',dict_values.get('account_payment_id'))])
        #                             if payment_id:
        #                                 check_payment = True

        #                                 worksheet.write(row, 0,payment_id.name,left_alignment)
        #                                 worksheet.write(row, 1,'',left_alignment)
        #                                 if move.partner_bank_id.acc_number:
        #                                     worksheet.write(row, 2,move.partner_bank_id.acc_number,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 2,'',center_alignment)

        #                                 if move.partner_bank_id.acc_holder_name:

        #                                     worksheet.write(row, 3,move.partner_bank_id.acc_holder_name,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 3,'',center_alignment)

        #                                 worksheet.write(row, 4,dict_values.get('amount'),center_alignment)


        #                                 worksheet.write(row, 5,'N',center_alignment)


        #                                 worksheet.write(row, 6,payment_id.date,format2)
        #                                 if move.partner_bank_id.bank_id.bic:

        #                                     worksheet.write(row, 7,move.partner_bank_id.bank_id.bic,center_alignment)

        #                                 else:
        #                                     worksheet.write(row, 7,'',center_alignment)

        #                                 worksheet.write(row, 8,move.name,left_alignment)


        #                                 row += 1

        #                         elif dict_values.get('move_id'):
        #                             move_id = move.env['account.move'].search([('move_type','=','entry'),('id','=',dict_values.get('move_id'))])
        #                             if move_id:
        #                                 check_payment = True

        #                                 worksheet.write(row, 0,move_id.name,left_alignment)
        #                                 worksheet.write(row, 1,'',left_alignment)
        #                                 if move.partner_bank_id.acc_number:
        #                                     worksheet.write(row, 2,move.partner_bank_id.acc_number,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 2,'',center_alignment)

        #                                 if move.partner_bank_id.acc_holder_name:

        #                                     worksheet.write(row, 3,move.partner_bank_id.acc_holder_name,center_alignment)
        #                                 else:
        #                                     worksheet.write(row, 3,'',center_alignment)

        #                                 worksheet.write(row, 4,dict_values.get('amount'),center_alignment)


        #                                 worksheet.write(row, 5,'N',center_alignment)


        #                                 worksheet.write(row, 6,move_id.date,format2)
        #                                 if move.partner_bank_id.bank_id.bic:

        #                                     worksheet.write(row, 7,move.partner_bank_id.bank_id.bic,center_alignment)

        #                                 else:
        #                                     worksheet.write(row, 7,'',center_alignment)

        #                                 worksheet.write(row, 8,move.name,left_alignment)





















        #                                 row += 1

                
        #         if check_payment:
        #             row += 1
                  
        worksheet.set_column('A:A',80)
        worksheet.set_column('A:B',18)
        worksheet.set_column('A:C',17)
        worksheet.set_column('A:D',15)
        worksheet.set_column('A:E',15)
        worksheet.set_column('A:F',20)
        worksheet.set_column('A:G',20)
        worksheet.set_column('A:H',20)
        worksheet.set_column('A:I',20)
        worksheet.set_column('A:G',20)
        worksheet.set_column('A:K',20)
        worksheet.set_column('A:L',20)
        worksheet.set_column('A:M',20)
        worksheet.set_column('A:N',20)
        worksheet.set_column('A:O',20)
        worksheet.set_column('A:P',20)
        worksheet.set_column('A:R',20)
        worksheet.set_column('A:S',20)
        worksheet.set_column('A:T',20)
        worksheet.set_column('A:U',20)
        worksheet.set_column('A:V',20)
       



        workbook.close()
        xlsx_data = output.getvalue()
      
        self.y_project_report = base64.encodebytes(xlsx_data)
        if self.y_choose_on == 'customer':
            self.y_file_name = 'Invoice Reconciliation Report.xlsx'
        else:
            self.y_file_name = 'Bill Reconciliation Report.xlsx'
        self.y_project_report_printed = True
        

        return {
        'name' : "Invoice/Bill Reconciliation Report",
        'view_mode': 'form',
        'res_id': self.id,
        'res_model': 'invoice.reconciliation.report.wizard',
        'view_type': 'form',
        'type': 'ir.actions.act_window',
        'context': self.env.context,
        'target': 'new',
                   }
