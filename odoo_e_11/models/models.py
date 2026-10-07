# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from lxml import etree
import re
import json
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang
from odoo.tools.float_utils import float_compare, float_round




class ProductTemplateNew(models.Model):
    _inherit = "product.template"

    y_product_warranty = fields.Boolean(string="Product Warranty")

class ProductProductNew(models.Model):
    _inherit = "product.product"

    y_product_warranty = fields.Boolean(string="Product Warranty")

class StockLotNew(models.Model):
    _inherit = "stock.lot"

    y_motor_id = fields.Char(string="Motor Id")

class ResbankdetailsCustomization(models.Model):
    _inherit = 'res.bank'
     
    @api.constrains('bic', 'name')
    def _check_unique_bic_name(self):
        for record in self:
            if self.search_count([('bic', '=', record.bic), ('name', '=', record.name), ('id', '!=', record.id)]) > 0:
                raise ValidationError('The combination of BIC and Bank Name must be unique.')
    
    
#     domastic_bool = fields.Boolean()
#     export_bool = fields.Boolean()






class Respartner(models.Model):
    _inherit = 'res.partner'

    y_iec_no=fields.Char(string="IEC NO")
    y_iec_date=fields.Date(string="IEC Date")
    y_lut_no=fields.Char(string="LUT No.")
    y_lut_valid_till=fields.Date(string="Lut Valid Till")
    y_reg_date=fields.Date(string ="Register Date")
    y_contact_person = fields.Char(string="Contact Person")

class SaleorderLine(models.Model):
    _inherit = "sale.order.line"

    y_is_free_sample = fields.Boolean(string="Free sample")

    def _prepare_invoice_line(self, **optional_values):

        res = super()._prepare_invoice_line()
        res['y_is_free_sample'] = self.y_is_free_sample
        
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    y_is_free_sample = fields.Boolean(string="Free sample")
    


class Saleordercustom(models.Model):
    _inherit = 'sale.order'

    y_po_ref=fields.Char(string="Po Ref")
    y_po_date=fields.Date(string="Po Date")
    y_shipping_method_id = fields.Many2one('shipping.method',string="Shipping Method")
    y_note = fields.Char(string="Note")
    
    y_bank_details = fields.Many2one('bank.details.export.domestic', string="Bank Details", domain="[('id', 'in', y_bank_details_domain)]",help="This Eruvaka Bank Account will be printed in this Record.",store=True)

    y_bank_details_domain = fields.Many2many('bank.details.export.domestic', compute='_compute_bank_details_domain')
    
    
    @api.depends('partner_id', 'company_id')
    def _compute_bank_details_domain(self):
        for record in self:
            domain = []
            if record.partner_id and record.company_id:
                if record.partner_id.country_id == record.company_id.country_id:
                    domain = record.company_id.y_domestic_bank_detail_ids.ids
                else:
                    domain = record.company_id.y_export_bank_detail_ids.ids

            record.y_bank_details_domain = [(6, 0, domain)]

            if domain:
                if record.y_bank_details.id not in domain:
                    record.y_bank_details = domain[0] if domain else False
            else:
                record.y_bank_details = False



    # def post_packing_details(self):
    #     print('1111111111111111111111111111111111111111111111')
    #     for rec in self:
    #         for move_line in rec.picking_ids.move_line_ids_without_package:
    #             if move_line.result_package_id and move_line.quantity > 0:
    #                 pack_val = self.env['packaging.list'].browse(self._context.get('ref_pack_id'))
    #                 pack_val.y_sale_order_ids = self.mapped('id')
    #                 net_weight = (move_line.product_id.product_tmpl_id.weight*move_line.quantity)
    #                 gross_weight = (move_line.result_package_id.shipping_weight + net_weight)
    #                 pack_val.y_packaging_list_ids = [(0,0,{
    #                     'y_product_id':move_line.product_id.id,
    #                     'y_product_description':move_line.product_id.name,
    #                     'y_sale_origin_id':rec.id,
    #                     'y_packing_stock_id':move_line.result_package_id.id,
    #                     'package_type_id':move_line.result_package_id.package_type_id.id,
    #                     'shipping_weight':move_line.result_package_id.shipping_weight,
    #                     'y_quantity':move_line.quantity,
    #                     'y_package_customer':pack_val.y_partner_id.id,
    #                     'y_customer_ref':pack_val.y_partner_id.ref,
    #                     'y_customer_po':rec.client_order_ref,
    #                     'y_net_weight':net_weight,
    #                     'y_gross_weight':gross_weight,
    #                     'y_kit_product': move_line.description_bom_line,
    #                     })]

class Accountmovecustom(models.Model):
    _inherit = 'account.move'

    y_lut_arn_nu=fields.Char(string ="LUT ARN NO")
    y_reg_date = fields.Date()
    y_valid_till=fields.Date(string ="Valid Till")
    y_export_ref_no = fields.Char(string="Export Ref No")
    y_export_ref_date = fields.Date(string="Export Date")
    y_e_o_e = fields.Char(string="EOE")
    y_note = fields.Char(string="Note")
    y_exchange_rate = fields.Float(string="Exchange Rate",digits=(12, 12))
    y_bank_details = fields.Many2one('bank.details.export.domestic', string="Bank Details", domain="[('id', 'in', y_bank_details_domain)]",help="This Eruvaka Bank Account will be printed in this Record.",store=True)

    y_bank_details_domain = fields.Many2many('bank.details.export.domestic', compute='_compute_bank_details_domain')
    
    
    def action_post(self):
        res = super(Accountmovecustom, self).action_post()
        for rec in self:
            exchange_rate = 1 / rec.invoice_line_ids[0].currency_rate
            rec.write({'y_exchange_rate': exchange_rate})
        return res
    
    
    @api.depends('partner_id', 'company_id')
    def _compute_bank_details_domain(self):
        for record in self:
            domain = []
            if record.partner_id and record.company_id:
                if record.partner_id.country_id == record.company_id.country_id:
                    domain = record.company_id.y_domestic_bank_detail_ids.ids
                else:
                    domain = record.company_id.y_export_bank_detail_ids.ids
            record.y_bank_details_domain = [(6, 0, domain)]
            if domain:
                if record.y_bank_details.id not in domain:
                    record.y_bank_details = domain[0] if domain else False
            else:
                record.y_bank_details = False
   
      
    # @api.onchange('partner_id', 'company_id')
    # def _onchange_bank_details(self):
    #     domain = {}
    #     if self.partner_id and self.company_id:
    #         if self.partner_id.country_id == self.company_id.country_id:
    #             # If the countries match, use domestic bank details
    #             if self.company_id.y_export_bank_detail_ids:
    #                 bank_details_export = self.company_id.y_export_bank_detail_ids
    #                 # print(account_name_export,"export name -----------------------------1")
    #                 return bank_details_export
    #         else:
    #             # If the countries do not match, use export bank details
    #             if self.company_id.y_export_bank_detail_ids:
    #                 domain = {'y_bank_details': [('id', 'in', self.company_id.y_export_bank_detail_ids.mapped('y_export_bank_detail_id.id'))]}
    #     return {'domain': domain}


class ResShippingMethodMenu(models.Model):
	_name = 'shipping.method'
	_description = 'Shipping Method'
	_rec_name = 'y_shipping_method'

	y_shipping_method = fields.Char(string="Shipping Method")


class Saleordercustom(models.Model):
    _inherit = 'purchase.order'

    y_notes = fields.Char(string="Notes") 
    y_vendor_code = fields.Char(related="partner_id.ref",string = "Vendor Code") 
    y_po_number = fields.Char(related="name",string = "PO Document Number")
    payment_term_id = fields.Many2one(tracking=True)
    currency_id = fields.Many2one(tracking=True)
    date_planned = fields.Datetime(tracking=True)
    picking_type_id = fields.Many2one(tracking=True)
    origin= fields.Char(tracking=True)
    incoterm_id = fields.Many2one(tracking=True)
    fiscal_position_id = fields.Many2one(tracking=True)
    y_warehouse_id = fields.Many2one(tracking=True)

    def write(self, vals):
        if vals.get('order_line'):
            new_list = []
            for list1 in vals.get('order_line'):
                if isinstance(list1, (list, tuple)) and len(list1) > 1:
                    # We are only interested in the update commands (usually indicated by [1, id, vals])
                    if list1[0] == 1 and isinstance(list1[2], dict):
                        new_list.append(list1)

            component_lines_ids = self.order_line.filtered(lambda x: x.id in [value[1] for value in new_list])
            for dicts in component_lines_ids:
                new_dist = []
                for newval in new_list:
                    if newval[1] == dicts.id:  # Ensure we're updating the correct line
                        update_vals = newval[2]  # Get the dictionary of values to be updated
                        if update_vals.get('price_unit'):
                            new_price_unit = update_vals.get('price_unit')
                            new_dist.append('{}{} ---> {}'.format("Unit Price :", dicts.price_unit, new_price_unit))
                        if update_vals.get('product_qty'):
                            new_quantity = update_vals.get('product_qty')
                            new_dist.append('{}{} ---> {}'.format("Quantity :", dicts.product_uom_qty, new_quantity))
                        if update_vals.get('product_uom'):
                            new_product_uom = self.env['uom.uom'].search([('id', '=', update_vals.get('product_uom'))], limit=1)
                            new_dist.append('{}{} ---> {}'.format("UOM :", dicts.product_uom.name, new_product_uom.name))
                        if new_dist:
                            msg = ', \n '.join(dic for dic in new_dist)
                            if self.env.user:
                                self.message_post(body=msg)
       
        res = super(Saleordercustom, self).write(vals)
        return res
    
class Purchaseorderlinecustom(models.Model):
    _inherit = 'purchase.order.line'

    def unlink(self):
        new_dist = []
        for order_line in self:
            if order_line.product_id:
                new_dist.append('{}'.format(order_line.product_id.name))
        if new_dist:
            msg = ', '.join(dic for dic in new_dist)
            msg = msg + ' ' +'Removed'
            order_id = self.mapped('order_id')
            if self.env.user:
                order_id.message_post(body=msg)                               

        res = super(Purchaseorderlinecustom,self).unlink()
        return res
    
    def write(self,vals):
        tax_ids = vals.get('taxes_id', [])

        if tax_ids:
            removed_dist = []
            added_list = []
            for tx in tax_ids:
                if tx:
                    if tx[0] == 3:
                        removed_tax_name = self.env['account.tax'].browse(tx[1]).name
                        removed_dist.append(removed_tax_name)
                    if tx[0] == 4:
                        added_tax_name = self.env['account.tax'].browse(tx[1]).name
                        added_list.append(added_tax_name)
            if removed_dist:
                removed_tax_name =  ', '.join(removed_dist)
                msg1 = "{} Removed: {}".format("Taxes",removed_tax_name)
                self.order_id.message_post(body=msg1)
            if added_list:
                added_tax_name =  ', '.join(added_list)
                msg2 = "{} Added: {}".format("Taxes",added_tax_name)
                self.order_id.message_post(body=msg2)

        res = super(Purchaseorderlinecustom, self).write(vals)
      


        return res
    
    def _get_select_sellers_params(self):
        self.ensure_one()
        return {
            "order_id": self.order_id,
        }

    @api.depends('product_qty', 'product_uom', 'company_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            params = {'order_id': line.order_id}
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params)

            if seller or not line.date_planned:
                line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not seller:
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)
                if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False
                )
                line.price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                               self.env[
                                                                                   'decimal.precision'].precision_get(
                                                                                   'Product Price')))

                # No seller case: Show display name + product description
                product_lang = line.product_id.with_context(
                    lang=get_lang(line.env, line.partner_id.lang).code
                )
                description = product_lang.description_purchase or product_lang.description or ''
                line.name = f"{line.product_id.display_name}\n{description}"
                continue

            price_unit = line.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                                 line.product_id.supplier_taxes_id,
                                                                                 line.taxes_id,
                                                                                 line.company_id) if seller else 0.0
            price_unit = seller.currency_id._convert(price_unit, line.currency_id, line.company_id,
                                                     line.date_order or fields.Date.context_today(line), False)
            price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                      self.env['decimal.precision'].precision_get(
                                                                          'Product Price')))
            line.price_unit = seller.product_uom._compute_price(price_unit, line.product_uom)
            line.discount = seller.discount or 0.0

            # Get default product display name (with internal reference)
            default_product_name = line.product_id.display_name

            # Get vendor-specific description
            if seller:
                product_ctx = {'seller_id': seller.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                vendor_description = line._get_product_purchase_description(line.product_id.with_context(product_ctx))

                # Check if the vendor has a product code
                vendor_has_code = seller.product_code and len(seller.product_code.strip()) > 0
                vendor_has_name = seller.product_name and len(seller.product_name.strip()) > 0

                if vendor_has_code and vendor_has_name:
                    # If vendor has code, the description includes [code]description format
                    line.name = f"{default_product_name},{vendor_description}"
                elif vendor_has_code and not vendor_has_name:
                    vendor_code = seller.product_code
                    line.name = f"{default_product_name}",[vendor_code]
                elif vendor_has_name and not vendor_has_code:
                    vendor_name = seller.product_name
                    line.name = f"{default_product_name},{vendor_name}"
                else:
                    line.name = default_product_name
            else:
                # If no seller, just use the default product name
                line.name = default_product_name
    



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    y_vehicle_no = fields.Char(string="Vehicle No")
    y_e_waybill_no = fields.Char(string="E-waybill No")
    y_res_state_id = fields.Many2one('res.country.state', string="State", related='partner_id.state_id')
    y_nature_of_supply = fields.Selection([
        ('inter_state', 'Inter State'),
        ('intra_state', 'Intra State'),
        ],copy=False,tracking=True,string="Nature Of Supply")
    y_note = fields.Char(string="Note")
    y_po_number = fields.Char(related="purchase_id.name",string = "PO Document Number",tracking=True)
    y_invoice_number = fields.Char(string="Invoice Number",tracking=True)
    y_date = fields.Date(string="Date",tracking=True)
   
    y_boolean_purchase_id = fields.Boolean(default=False,compute="readonly_for_fields" ,string = "Boolean Purchase")

    def button_validate(self):
        for picking in self:
            if not picking.y_invoice_number:
                raise ValidationError("Please fill Invoice number")
            if not picking.y_date:
                raise ValidationError("Please fill Date")

        res = super(StockPicking, self).button_validate()
        for picking in self:
            for stock_move_line in picking.move_line_ids_without_package:
                if stock_move_line.lot_id and stock_move_line.y_motor_id:
                    stock_move_line.lot_id.y_motor_id = stock_move_line.y_motor_id


                    

        return res
    

    def readonly_for_fields(self):
        for rec in self:
            if rec.purchase_id.picking_type_id.code in ('outgoing','incoming'):
                rec.y_boolean_purchase_id = True
               
            else:
                rec.y_boolean_purchase_id = False

    
 
class StockPackaging(models.Model):
    _inherit = 'stock.quant.package'

    y_kit_product = fields.Char(string="Kit")

class packagingList(models.Model):
    _inherit = 'packaging.list'

    y_note = fields.Char(string="Note")

class Stockmoveline(models.Model):
    _inherit = 'stock.move.line'


    y_vender_serial_no = fields.Char(string="Vendor Serial No." ,store=True)
    y_motor_id = fields.Char(string="Motor Id")
    
class packagingList(models.Model):
    _inherit = 'packaging.list'

    y_note = fields.Char(string="Note")

class PurchaseOrderCancel(models.Model):
    _inherit = 'purchase.order'
    
  
    y_cancel_reason_id = fields.Char(string='Cancel Reason', size=50)
    y_is_cancel = fields.Boolean(string="Is Cancel")
    

    def button_cancel(self):
        if self.state in ('draft', 'sent', 'to approve', 'purchase'):
            return {
                    'name': 'Cancel Reason',
                    'type': 'ir.actions.act_window',
                    'res_model': 'in.cancel.reason.wizard.purchase',
                    'view_mode': 'form',
                    'view_id': self.env.ref('odoo_e_11.in_cancel_wizard_purchase').id,
                    'target':'new',           
                }    
        else:
            result = super(PurchaseOrderCancel, self).button_cancel()
            return result          


    
    
class BankDetailForExportandDomestic(models.Model):
    _name = 'bank.details.export.domestic'  
    _description = 'Bank Details for Export and Domestic'
    _rec_name= 'y_record_name'
    
    

    y_domestic_acc_number = fields.Char(string="Domestic Account Number", compute='_compute_account_numbers', store=True)
    y_domestic_acc_number_update = fields.Many2one('res.partner.bank')
    y_export_acc_number = fields.Char(string="Export Account Number", compute='_compute_account_numbers', store=True)
    y_export_acc_number_update = fields.Many2one('res.partner.bank')

    @api.depends('y_domestic_acc_number_update', 'y_export_acc_number_update')
    def _compute_account_numbers(self):
        for record in self:
            record.y_domestic_acc_number = record.y_domestic_acc_number_update.acc_number if record.y_domestic_acc_number_update else ''
            record.y_export_acc_number = record.y_export_acc_number_update.acc_number if record.y_export_acc_number_update else ''
            
    
    # @api.depends('y_domestic_acc_number_update', 'y_export_acc_number_update')
    # def _compute_account_numbers(self):
    #     for record in self:
    #         record.y_domestic_acc_number = self._extract_account_number(record.y_domestic_acc_number_update)
    #         record.y_export_acc_number = self._extract_account_number(record.y_export_acc_number_update)

    # def _extract_account_number(self, bank_record):
    #     print(bank_record,"kkkkkkkkkkkkkkkkkkkkkkkkkk",bank_record.display_name)
    #     if bank_record:
    #         account_info = bank_record.display_name or ""
    #         match = re.match(r'(\d+)', account_info)
    #         print(match,"kkkkkkkkkkkkkkkkkkkssssssssssssssssss",match.group(1))
    #         print(bank_record.acc_number,222222222222222222222222222222222222222)
    #         if match:
    #             return match.group(1)
    #     return ''
    
    
    
    
    
    y_export_bank_detail_id = fields.Many2one('res.company', string="Bank Detail")
   
    y_export_bank_id = fields.Many2one('res.bank',tracking=True,string="Bank")
    y_export_acc_holder_name = fields.Char(tracking=True,string="Account Holder")
   
    y_domestic_bank_detail_id = fields.Many2one('res.company', string="Bank Detail")
    
    y_domestic_bank_id = fields.Many2one('res.bank',tracking=True,string="Bank")
    y_domestic_acc_holder_name = fields.Char(tracking=True,string="Account Holder")
    
    y_record_name = fields.Char(compute="_compute_record_name", store=True,string="Bank Name")
    
    @api.onchange('y_export_acc_number_update','y_domestic_acc_number_update')
    def _onchange_acc_number(self):
        for rec in self:
            if rec.y_export_acc_number_update:
               rec.y_export_bank_id = rec.y_export_acc_number_update.bank_id
               rec.y_export_acc_holder_name = rec.y_export_acc_number_update.acc_holder_name
            else:
                rec.y_domestic_bank_id = rec.y_domestic_acc_number_update.bank_id
                rec.y_domestic_acc_holder_name = rec.y_domestic_acc_number_update.acc_holder_name
                
    

    @api.depends('y_export_bank_id', 'y_export_acc_number_update.acc_number', 'y_domestic_bank_id', 'y_domestic_acc_number_update.acc_number')
    def _compute_record_name(self):
        for record in self:
            if record.y_export_bank_id and record.y_export_acc_number_update.acc_number:
                record.y_record_name = f"{record.y_export_bank_id.name} - {record.y_export_acc_number_update.acc_number}"
            elif record.y_domestic_bank_id and record.y_domestic_acc_number_update.acc_number:
                record.y_record_name = f"{record.y_domestic_bank_id.name} - {record.y_domestic_acc_number_update.acc_number}"
            elif record.y_export_bank_id:
                record.y_record_name = record.y_export_bank_id.name
            elif record.y_domestic_bank_id:
                record.y_record_name = record.y_domestic_bank_id.name
            else:
                record.y_record_name = "No Bank Details"

    def name_get(self):
        result = []
        for rec in self:
            name = rec.y_record_name
            result.append((rec.id, name))
        return result
        
class respartnercustom(models.Model):
    _inherit = 'res.company'
    
    y_export_bank_detail_ids = fields.One2many('bank.details.export.domestic','y_export_bank_detail_id', string="Export Bank Details")
    y_domestic_bank_detail_ids = fields.One2many('bank.details.export.domestic','y_domestic_bank_detail_id', string="Domestic Bank Details")

