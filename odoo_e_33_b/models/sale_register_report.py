
from decimal import FloatOperation
import re
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from xlwt import easyxf
from odoo.exceptions import UserError, ValidationError
import xlwt
import io
import base64
import datetime
import math
import json
from odoo.tools.float_utils import float_round, float_is_zero
from odoo import tools


class SalesRegisterReport(models.Model):
    _name = "sales.register.report"
    _auto = False
    _description =  " "


    
    y_journal_id = fields.Many2one('account.journal', 'Journal Name',readonly=True)
    y_account_id = fields.Many2one('account.account','Account Name',readonly=True)
    y_move_id = fields.Many2one('account.move',string='Invoice Number')
    y_move_line_id = fields.Many2one('account.move.line')
    y_invoice_date = fields.Date(string='Invoice Date')
    y_currency_id = fields.Many2one('res.currency', string="Currency",readonly=True)

    y_sale_order_id = fields.Many2one('sale.order',string="Sale Order Number")
    y_sale_line_id = fields.Many2one('sale.order.line',string="Sale Order line")
    y_sale_order_date = fields.Datetime(string="Sale Order Date")
    y_is_free_sample = fields.Boolean(string="Free sample")


    y_move_type_name = fields.Selection([
            ('entry','Journal Entry'),
            ('out_invoice', 'Customer Invoice'),    
            ('out_refund' , 'Customer Credit Note'),
            ('in_invoice' , 'Vendor Bill'),
            ('in_refund' ,'Vendor Credit Note'),  
            ('out_receipt' ,'Sales Receipt' ),  
            ('in_receipt'  ,'Purchase Receip'),],string='Invoice Type')
    
    y_vendor_bill_ref = fields.Char(string="Vendor Bill Reference")
    y_vendor_entry_ref = fields.Char(string="Vendor Entry	Reference")


    # Partner relate fields
    y_partner_id = fields.Many2one('res.partner',string="Partner")
    y_partner_city = fields.Char(string="Customer City")
    y_partner_state_id = fields.Many2one('res.country.state',string="Customer State")
    y_partner_country_id = fields.Many2one('res.country',string="Customer Country")
    y_gst_name = fields.Char(string="Customer GST No")
    y_partner_ref = fields.Char(string="Customer Code")
    y_sales_person_id = fields.Many2one('res.users',string="Sales person")
    y_sales_team_id = fields.Many2one('crm.team',string="Sales Team")

    y_partner_shipping_id = fields.Char('res.partner')
    y_partner_shipping_state_id = fields.Many2one('res.country.state',string="Vendor State")
    y_vat = fields.Char(string="Vendor GST No")

    # Product relate fields
    y_product_id = fields.Many2one('product.product', string="Product")
    y_label = fields.Char(string="Label") # invoice_line.name
    y_uom_id = fields.Many2one('uom.uom',string="Product Uom")
    y_hsn_code = fields.Char(string="HSN Code")
    y_product_category_id = fields.Many2one('product.category',string="Product Category")
    # y_item_group_id= fields.Many2one('item.group',string="Item Group")
    # y_product_group_1_id = fields.Many2one('product.group.1',string="Product Group 1")
    # y_product_group_2_id = fields.Many2one('product.group.2',string="Product Group 2")
    # y_product_group_3_id = fields.Many2one('product.group.3',string="Product Group 3")
    y_product_ref = fields.Char(string="Product Code")
    product_type = fields.Selection([
        ('product', 'Storable Product'),
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type')




    y_invoice_amount_fc = fields.Float(string='Invoice Amount FC')
    y_quantity = fields.Float('Quantity',readonly=True)
    y_price_unit = fields.Float('Unit Price',readonly=True)
    y_price_subtotal = fields.Float('Subtotal')

    y_analytic_account_ids = fields.Many2many('account.analytic.account',compute="get_analytic_distribution",string="Analytical Account")
    y_amount_exclusive_tax = fields.Float(string="Amount Exclusive Tax",compute="_compute_y_amount_exclusive_tax") 
    y_amount_inclusive_tax = fields.Float(string="Amount Inclusive Tax",compute="compute_y_amount_inclusive_tax")

    y_cgst_percent = fields.Float(compute="report_compute_tax", string="CGST Rate %",readonly=True)
    y_cgst_amount = fields.Float(compute="report_compute_tax", string="CGST Amount",readonly=True)
    y_sgst_percent = fields.Float(compute="report_compute_tax", string="SGST Rate %",readonly=True)
    y_sgst_amount = fields.Float(compute="report_compute_tax", string="SGST Amount",readonly=True)
    y_igst_percent = fields.Float(compute="report_compute_tax", string="IGST Rate %",readonly=True)
    y_igst_amount = fields.Float(compute="report_compute_tax", string="IGST Amount",readonly=True)    
    y_tds_percent = fields.Float(compute="report_compute_tax", string="TDS Rate %",readonly=True)
    y_tds_amount = fields.Float(compute="report_compute_tax", string="TDS Amount",readonly=True)
    y_tcs_percent = fields.Float(string="TCS Rate %",compute="report_compute_tax")
    y_tcs_amount = fields.Float(string="TCS Amount",compute="report_compute_tax")
    y_rcm_percent = fields.Float(string="RCM Rate %",compute="report_compute_tax")
    y_rcm_amount = fields.Float(string="RCM Amount",compute="report_compute_tax")
    y_ocean_tax_percent = fields.Float(string="Ocean Tax Rate",compute="report_compute_tax")
    y_ocean_tax_amount = fields.Float(string="Ocean Tax Amount",compute="report_compute_tax")

    y_tax_amount = fields.Float(compute="total_tax", string="Total Tax Amount",readonly=True)
    y_tax_id_list = fields.Char('List of Tax Id')

    y_discount = fields.Float(string="Discount %")

    y_payment_state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('partial', 'Partially Paid'),
            ('reversed', 'Reversed'),
            ('invoicing_legacy', 'Invoicing App Legacy'),
        ],
        string="Payment State")

    # Computing the taxes
    def report_compute_tax(self):
        for record in self:
            y_tds_percent = 0.0
            y_cgst_percent = 0.0
            y_sgst_percent = 0.0
            y_igst_percent = 0.0
            y_tds_amount = 0.0
            y_sgst_amount = 0.0
            y_cgst_amount = 0.0
            y_igst_amount = 0.0

            y_tcs_percent = 0.0
            y_tcs_amount = 0.0
            y_rcm_percent = 0.0
            y_ocean_tax_percent = 0.0

            total_percent = 0.0
        
            for tax in self.env['account.tax'].browse(record.y_tax_id_list):
                y_ocean_tax_amount = 0.0
                y_rcm_amount = 0.0
                if tax.amount_type == 'group':
                    grp_sgst = []
                    grp_cgst = []
                    grp_igst = []
                    grp_tds = []

                    grp_tcs = []
                    total_tax = 0.0

                    for child_tax in tax.children_tax_ids:
                       
                        if child_tax.tax_group_id.name == 'CGST':
                            grp_cgst.append(child_tax.amount)
                        elif child_tax.tax_group_id.name == 'SGST':
                            grp_sgst.append(child_tax.amount)
                        elif child_tax.tax_group_id.name == 'IGST':
                            grp_igst.append(child_tax.amount)
                        elif child_tax.tax_group_id.name == 'TDS':
                            grp_tds.append(child_tax.amount)
                        elif child_tax.tax_group_id.name == 'TCS':
                            grp_tcs.append(child_tax.amount)   

                        elif child_tax.tax_group_id.name == 'RCM':
                            for rcm_per in child_tax.children_tax_ids:
                                y_rcm_percent += abs(rcm_per.amount)/2 if rcm_per.amount else 0.00
                                y_rcm_amount += record.y_move_line_id.price_subtotal*rcm_per.amount/100
                        elif child_tax.tax_group_id.name == 'OCEAN':
                            for ocean_per in child_tax.children_tax_ids:
                                y_ocean_tax_percent += abs(ocean_per.amount)/2
                                y_ocean_tax_amount += record.y_move_line_id.price_subtotal*ocean_per.amount/100     


                    y_tds_percent += sum(grp_tds)
                    y_cgst_percent += sum(grp_cgst)
                    y_sgst_percent += sum(grp_sgst)
                    y_igst_percent += sum(grp_igst)

                    y_tcs_percent +=sum(grp_tcs)
                    
                    y_cgst_amount += (record.y_price_subtotal * (sum(grp_cgst)/ 100))
                    y_sgst_amount += (record.y_price_subtotal * (sum(grp_sgst)/ 100))
                    y_igst_amount += (record.y_price_subtotal * (sum(grp_igst)/ 100))

                    y_tcs_amount += (record.y_price_subtotal * (sum(grp_tcs)/ 100))

                    if grp_tds != []:
                        total_percent += sum([y_cgst_amount, y_sgst_amount, y_igst_amount])
                        y_tds_amount += ((record.y_price_unit * record.y_quantity)/100)* sum(grp_tds)


                else:
                    res = record.y_move_line_id.tax_ids.compute_all(product=record.y_move_line_id.product_id,quantity=record.y_move_line_id.quantity,price_unit=record.y_move_line_id.price_unit)
                    gst_value = res['taxes']
                    if tax.tax_group_id.name == 'CGST':
                        y_cgst_amount +=  (record.y_price_subtotal * (tax.amount/ 100))
                        y_cgst_percent += tax.amount    
                    elif tax.tax_group_id.name == 'SGST':
                        y_sgst_amount += (record.y_price_subtotal * (tax.amount/ 100))
                        y_sgst_percent += tax.amount
                    elif tax.tax_group_id.name == 'IGST':
                        y_igst_amount +=(record.y_price_subtotal * (tax.amount/ 100))
                        y_igst_percent += tax.amount
                    elif tax.tax_group_id.name == 'TDS':
                        y_tds_amount += (record.y_price_subtotal * (tax.amount/ 100))
                        y_tds_percent += tax.amount

                    elif tax.tax_group_id.name == 'TCS':
                        for list_tax in gst_value:
                            check_tax_id = list_tax.get('id')
                            if tax.id == check_tax_id:
                                y_tcs_amount += float_round(list_tax.get('amount'),2)
                                y_tcs_percent  = tax.amount

            tot_tax_amt = y_tds_amount + y_sgst_amount + y_cgst_amount + y_igst_amount
            record.y_tds_percent = y_tds_percent
            record.y_sgst_percent = y_sgst_percent
            record.y_cgst_percent = y_cgst_percent 
            record.y_igst_percent = y_igst_percent 
            record.y_sgst_amount = y_sgst_amount
            record.y_cgst_amount = y_cgst_amount
            record.y_igst_amount = y_igst_amount 
            record.y_tds_amount = y_tds_amount
            record.y_tcs_percent = y_tcs_percent
            record.y_tcs_amount = y_tcs_amount
            record.y_rcm_percent = y_rcm_percent
            record.y_rcm_amount = y_rcm_amount
            record.y_ocean_tax_percent = y_ocean_tax_percent
            record.y_ocean_tax_amount = y_ocean_tax_amount
  
    
    # Total Tax
    def total_tax(self):
        for itm in self:
            itm.y_tax_amount = sum([itm.y_tds_amount,itm.y_sgst_amount,itm.y_cgst_amount,itm.y_igst_amount,itm.y_tcs_amount,itm.y_rcm_amount,itm.y_ocean_tax_amount])
    # Amount Inclusive Tax
    def compute_y_amount_inclusive_tax(self):
        for itm in self:
            itm.y_amount_inclusive_tax = sum([itm.y_tax_amount,itm.y_amount_exclusive_tax])

    # Amount Exclusive Tax
    def _compute_y_amount_exclusive_tax(self):
        for rec in self:
            rec.y_amount_exclusive_tax = 0            
            if rec.y_move_id.currency_id == rec.y_move_id.company_id.currency_id:
                rec.y_amount_exclusive_tax = rec.y_move_line_id.price_subtotal
            else:
                if rec.y_move_id.move_type == 'in_refund':
                    rec.y_amount_exclusive_tax = rec.y_move_line_id.credit
                elif rec.y_move_id.move_type == 'in_invoice':
                    rec.y_amount_exclusive_tax = rec.y_move_line_id.debit
    
    # Amount Analytical Account
    def get_analytic_distribution(self):
        for rec in self:
            rec.y_analytic_account_ids = False
            if rec.y_move_line_id.analytic_distribution:
                analytic_ids = []
                for analytic_key in rec.y_move_line_id.analytic_distribution.keys():
                    int_analytic_key = int(analytic_key)
                    analytic_account_obj = rec.env['account.analytic.account'].browse(int_analytic_key)
                    if analytic_account_obj.active:
                        analytic_ids.append(analytic_account_obj.id)
                rec.y_analytic_account_ids = analytic_ids

    @api.model
    def sale_register_query(self, start_date, end_date):
        allowed_company_ids = self.env.context.get('allowed_company_ids', [])

        # Ensure it's a tuple if there's only one company (SQL requires a tuple format for IN)
        if isinstance(allowed_company_ids, int):
            allowed_company_ids = (allowed_company_ids,)
        elif isinstance(allowed_company_ids, list):
            allowed_company_ids = tuple(allowed_company_ids)

        tools.drop_view_if_exists(self._cr, 'sales_register_report')
        self._cr.execute("""
                CREATE OR REPLACE VIEW sales_register_report AS (
                    SELECT 
                    row_number() OVER () as id,
                    move.move_type AS y_move_type_name,
                    move.id AS y_move_id,
                    move.invoice_date AS y_invoice_date,
                    move.payment_state AS y_payment_state,
                    move.name AS y_vendor_entry_ref,
                    move.ref AS y_vendor_bill_ref,
                    move.invoice_user_id AS y_sales_person_id,
                    move.team_id AS y_sales_team_id,
                    line.name AS y_label,
                    (CASE WHEN res_curr.name != 'INR' THEN (line.price_subtotal) END) AS y_invoice_amount_fc,
                    so.name,
                    move.invoice_origin,
                    sol.id AS y_sale_line_id,
                    so.id AS y_sale_order_id,
                    so.date_order AS y_sale_order_date,
                    line.product_id AS y_product_id,
                    pt.id AS product_tmpl_id,
                    pt.detailed_type AS product_type,
                    uom.id AS y_uom_id,
                    pro_categ.id AS y_product_category_id,
                    line.id AS y_move_line_id,
                    line.quantity AS y_quantity,
                    line.price_unit AS y_price_unit,
                    line.price_subtotal AS y_price_subtotal,
                    line.y_is_free_sample AS y_is_free_sample,
                    line.journal_id AS y_journal_id,
                    line.account_id AS y_account_id,
                    array_agg(tax_rel.account_tax_id) AS y_tax_id_list,
                    line.partner_id AS y_partner_id,
                    line.currency_id AS y_currency_id,
                    line.discount AS y_discount,
                    partner.ref AS y_partner_ref,
                    partner.state_id AS y_partner_state_id,
                    partner.city AS y_partner_city,
                    partner.vat AS y_gst_name,
                    partner.country_id AS y_partner_country_id,
                    rp.name as y_partner_shipping_id,
                    rp.state_id as y_partner_shipping_state_id,
                    rp.vat as y_vat,
                    pt.l10n_in_hsn_code AS y_hsn_code,
                    product.default_code as y_product_ref 
                    FROM account_move move
                    JOIN account_move_line line ON move.id = line.move_id
                    -- Join with the sale_order_line_invoice_rel table to get related sale order lines
                    JOIN sale_order_line_invoice_rel sol_rel ON sol_rel.invoice_line_id = line.id
                    -- Join with sale order lines
                    JOIN sale_order_line sol ON sol.id = sol_rel.order_line_id
                    -- Join with sale orders
                    JOIN sale_order so ON so.id = sol.order_id
                    LEFT JOIN res_partner partner ON partner.id = move.partner_id
                    LEFT JOIN res_partner rp ON rp.id = move.partner_shipping_id
                    LEFT JOIN product_product product ON product.id = line.product_id
                    LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                    LEFT JOIN product_category pro_categ ON pro_categ.id = pt.categ_id
                    LEFT JOIN uom_uom uom ON uom.id = pt.uom_id
                    LEFT JOIN res_currency res_curr ON res_curr.id = line.currency_id
                    LEFT JOIN account_move_line_account_tax_rel tax_rel ON line.id = tax_rel.account_move_line_id
                    WHERE move.state = 'posted' 
                        AND line.product_id IS NOT NULL 
                        AND (move.move_type = 'out_invoice' OR move.move_type = 'out_refund') 
                        AND move.date BETWEEN %(start_date)s AND %(end_date)s
                        AND move.company_id IN %(companies)s
                    GROUP BY res_curr.name, line.name, line.id, sol.id, so.id, partner.city, pro_categ.id, pt.id, pt.detailed_type, pt.l10n_in_hsn_code, uom.id, 
                            move.move_type, move.id, line.quantity, line.price_unit, line.discount,
                            rp.state_id, rp.vat, rp.name, line.price_subtotal, line.journal_id, line.account_id, line.partner_id, line.currency_id, line.date,
                            move.payment_state, move.move_type, move.ref, partner.ref, partner.vat, partner.state_id, partner.country_id,
                            line.product_id, product.default_code, move.name
                )""", {
            'start_date': start_date,
            'end_date': end_date,
            'companies': allowed_company_ids
        })

        return {
            'name': _("Sale Register Report List"),
            'type': 'ir.actions.act_window',
            'res_model': 'sales.register.report',
            'view_mode': 'tree,pivot',
            'views': [(self.env.ref('odoo_e_33_b.view_sale_register_report_list').id, 'tree'),
                      (False, 'pivot')],
            'target': 'current',
        }

    # @api.model
    # def sale_register_query(self, start_date, end_date):
    #     allowed_company_ids = self.env.context.get('allowed_company_ids', [])
    #
    #     # Ensure it's a tuple if there's only one company (SQL requires a tuple format for IN)
    #     if isinstance(allowed_company_ids, int):
    #         allowed_company_ids = (allowed_company_ids,)
    #     elif isinstance(allowed_company_ids, list):
    #         allowed_company_ids = tuple(allowed_company_ids)
    #
    #     tools.drop_view_if_exists(self._cr, 'sales_register_report')
    #     self._cr.execute("""
    #         CREATE OR REPLACE VIEW sales_register_report AS (
    #             SELECT
    #             row_number() OVER () as id,
    #             move.move_type AS y_move_type_name,
    #             move.id AS y_move_id,
    #             move.invoice_date AS y_invoice_date,
    #             move.payment_state AS y_payment_state,
    #             move.name AS y_vendor_entry_ref,
    #             move.ref AS y_vendor_bill_ref,
    #             move.invoice_user_id AS y_sales_person_id,
    #             move.team_id AS y_sales_team_id,
    #             line.name AS y_label,
    #             (CASE WHEN res_curr.name != 'INR' THEN (line.price_subtotal) END) AS y_invoice_amount_fc,
    #             so.name,
    #             move.invoice_origin,
    #             sl.id AS y_sale_line_id,
    #             so.id AS y_sale_order_id,
    #             so.date_order AS y_sale_order_date,
    #             line.product_id AS y_product_id,
    #             pt.id AS product_tmpl_id,
    #             pt.detailed_type AS product_type,
    #             uom.id AS y_uom_id,
    #             pro_categ.id AS y_product_category_id,
    #             line.id AS y_move_line_id,
    #             line.quantity AS y_quantity,
    #             line.price_unit AS y_price_unit,
    #             line.price_subtotal AS y_price_subtotal,
    #             line.y_is_free_sample AS y_is_free_sample,
    #             line.journal_id AS y_journal_id,
    #             line.account_id AS y_account_id,
    #             array_agg(tax_rel.account_tax_id) AS y_tax_id_list,
    #             line.partner_id AS y_partner_id,
    #             line.currency_id AS y_currency_id,
    #             line.discount AS y_discount,
    #             partner.ref AS y_partner_ref,
    #             partner.state_id AS y_partner_state_id,
    #             partner.city AS y_partner_city,
    #             partner.vat AS y_gst_name,
    #             partner.country_id AS y_partner_country_id,
    #             rp.name as y_partner_shipping_id,
    #             rp.state_id as y_partner_shipping_state_id,
    #             rp.vat as y_vat,
    #             pt.l10n_in_hsn_code AS y_hsn_code,
    #             product.default_code as y_product_ref
    #             FROM account_move move
    #             LEFT JOIN account_move_line line ON move.id = line.move_id
    #             LEFT JOIN sale_order so on so.name = move.invoice_origin
    #             LEFT JOIN sale_order_line sl ON sl.order_id = so.id
    #             LEFT JOIN res_partner partner ON partner.id = move.partner_id
    #             LEFT JOIN res_partner rp on rp.id = move.partner_shipping_id
    #             LEFT JOIN product_product product ON product.id = line.product_id
    #             LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
    #             LEFT JOIN product_category pro_categ ON pro_categ.id = pt.categ_id
    #             LEFT JOIN uom_uom uom ON uom.id = pt.uom_id
    #             LEFT JOIN res_currency res_curr ON res_curr.id = line.currency_id
    #             LEFT JOIN account_move_line_account_tax_rel tax_rel ON line.id  = tax_rel.account_move_line_id
    #             WHERE move.state = 'posted'
    #                 AND line.product_id IS NOT NULL
    #                 AND (move.move_type = 'out_invoice' OR move.move_type = 'out_refund')
    #                 AND move.date BETWEEN %(start_date)s AND %(end_date)s
    #                 AND move.company_id IN %(companies)s
    #             GROUP BY res_curr.name, line.name, line.id, sl.id, so.id, partner.city, pro_categ.id, pt.id, pt.detailed_type, pt.l10n_in_hsn_code, uom.id,
    #                     move.move_type, move.id, line.quantity, line.price_unit, line.discount,
    #                     rp.state_id, rp.vat, rp.name, line.price_subtotal, line.journal_id, line.account_id, line.partner_id, line.currency_id, line.date,
    #                     move.payment_state, move.move_type, move.ref, partner.ref, partner.vat, partner.state_id, partner.country_id,
    #                     line.product_id, product.default_code, move.name
    #         )""", {
    #         'start_date': start_date,
    #         'end_date': end_date,
    #         'companies': allowed_company_ids
    #     })
    #
    #
    #     return {
    #         'name': _("Sale Register Report List"),
    #
    #         'type': 'ir.actions.act_window',
    #
    #         'res_model': 'sales.register.report',
    #
    #         'view_mode': 'tree,pivot',
    #
    #
    #         'views': [(self.env.ref('odoo_e_33_b.view_sale_register_report_list').id, 'tree'),(False, 'pivot')],
    #
    #         'target': 'current',
    #     }
