from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo import api, fields, models, _
from num2words import num2words
from calendar import monthrange
from lxml import etree
from odoo.tools import float_compare, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.exceptions import UserError, ValidationError
import math

class PackingListGroup(models.Model):
    _name = "packing.list.group"
    _description = "Packing List Group"
    _rec_name = "y_group"
    
    
    y_group = fields.Integer(string="Group Number", required=True, unique=True)
    
    
    _sql_constraints = [
        ('unique_y_group', 'unique(y_group)', 'Group number must be unique.')
    ]
    
    @api.constrains('y_group')
    def _check_y_group(self):
        for record in self:
            if record.y_group <= 0:
                raise ValidationError("Group number must be a positive integer.")





class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for move_lines in self.move_line_ids_without_package:
            if move_lines.result_package_id:
                move_lines.result_package_id.quant_ids.filtered(lambda x:x.product_id == move_lines.product_id).y_product_packaging_id = move_lines.move_id.product_packaging_id.id
                move_lines.result_package_id.quant_ids.filtered(lambda x:x.product_id == move_lines.product_id).y_kit_product = move_lines.description_bom_line
                move_lines.result_package_id.quant_ids.filtered(lambda x:x.product_id == move_lines.product_id).package_id.y_sale_origin_id = move_lines.move_id.picking_id.sale_id
        return res

class PortCodeCUstom(models.Model): 
    _inherit = "l10n_in.port.code"

    def name_get(self):
        result = None 
        for rec in self:
            if rec.code:
                result = '%s' % (rec.name)
            else:
                result = None 
        return result
    
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name_get()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    package_id = fields.Many2one(
        'stock.quant.package', 'Package',
        ondelete='restrict', check_company=True, index=True)


class StockPackaging(models.Model):
    _name = 'stock.quant.package'
    _inherit = ['stock.quant.package','mail.thread', 'mail.activity.mixin']

    y_net_weight = fields.Float(string="Net Weight",compute='_compute_weights', store=True)
    
    y_partner_id = fields.Many2one('res.partner',string="Customer",tracking=True,)
    y_partner_shipping_id = fields.Many2one('res.partner', string="Delivery Address",tracking=True)
    y_country_orgin_goods_id = fields.Many2one('res.country',string="Country of origin",tracking=True,related='y_sale_origin_id.y_country_orgin_goods_id')
    y_country_final_destination_id = fields.Many2one('res.country',string="Country of Final Destination",tracking=True,related='y_sale_origin_id.y_country_final_destination_id')
    y_pre_carriage = fields.Selection('Pre Carriage',copy=False,tracking=True,related='y_sale_origin_id.y_pre_carriage')
    y_vessel_number = fields.Char(string="Vessel/Flight No",tracking=True,related='y_sale_origin_id.y_vessel_number')
    y_port_loading_id = fields.Many2one('l10n_in.port.code',string="Port of Loading",tracking=True,related='y_sale_origin_id.y_port_loading_id')
    y_port_discharge_id = fields.Many2one('l10n_in.port.code',string="Port of Discharge",tracking=True,related='y_sale_origin_id.y_port_discharge_id')
    y_export_type = fields.Selection(string='Export Type',tracking=True,related='y_sale_origin_id.y_export_type_new')
    y_final_destination_id = fields.Many2one('res.country',string="Final Destination",related='y_sale_origin_id.y_final_destination_id')
    y_kit_product = fields.Char(string="Kit Product")

    y_state = fields.Selection(
        [('open','Open'),
        ('inprogress', 'Inprogress'),
        ('validated', 'Validated'),
        ],readonly=True, default='open', tracking=True,string='Status')
    y_invoice_ids = fields.Many2many('account.move', string='Invoices',readonly=True)
    y_invoice_date = fields.Date(string="Invoice Date")

    y_packaging_line_ids = fields.One2many('stock.quant.package.line','y_stock_quant_package_id',string="PackagingList Ids")
    y_notes = fields.Html('Terms and Conditions')
    y_container_number = fields.Char(string="Container No",tracking=True)
    y_container_seal_number = fields.Char(string="Container Seal No",tracking=True)
    y_volumetric_weight = fields.Selection([('5000','5000'),('6000','6000')],string="Volumetric Weight")
    y_quantity = fields.Float(string="Quantity")
    y_note = fields.Text(string="Note")
    
    y_warehouse_id = fields.Many2one("stock.warehouse",string="Warehouse",store=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id, index=1,readonly=False)
    
    y_sale_kit_line_ids = fields.One2many('sale.order.kit.line', 'y_sale_stock_quant_id', string='Package Lines')

    # standard field copy to add compute function
    shipping_weight = fields.Float(string='Shipping Weight', help="Total weight of the package.",compute='_compute_weights')
    
    @api.onchange('y_sale_origin_id')
    def update_sale_kit_lines(self):
        for rec in self:
            lines = []
            if rec.y_sale_origin_id:
                for line in rec.y_sale_origin_id.order_line:
                    print(line.product_template_id.name)
                    lines.append((0, 0, {
                        'y_sale_kit_id': line.product_template_id.id,
                        'y_kit_quantity': 0.0,  # Use the quantity from the sale order line
                    }))
            rec.y_sale_kit_line_ids = lines

    


    @api.depends('quant_ids.y_net_weight', 'quant_ids.y_gross_weight','quant_ids.quantity')
    def _compute_weights(self):
        for package in self:
            net_weight = sum(package.quant_ids.mapped('y_net_weight'))
            gross_weight = sum(package.quant_ids.mapped('y_gross_weight'))
            quantity = sum(package.quant_ids.mapped('quantity'))
            package.y_net_weight = net_weight
            package.y_quantity = quantity
            package.shipping_weight = gross_weight


    def get_package_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("odoo_e_47.button_get_package_lines_form_action")
        action['context'] = {
            'default_y_package_id': self.id,
            }
        return action
       


    def detailed_package_tracking(self):
        tree_view_id = self.env.ref('odoo_e_47.stock_quant_package_line_view').id
        if self.y_state == 'validated':
            context = {'create':False}
        else:
            context = {'ref_quant_id':self.id,'default_y_stock_quant_package_id':self.id,'default_y_stock_quant_id_quant_ids_product_ids':self.quant_ids.mapped('product_id').ids}
        return {
                'name': "Packaging List",
                'res_model': 'stock.quant.package.line',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'view_id': self.env.ref("odoo_e_47.stock_quant_package_line_view").id,
                'views': [[tree_view_id, 'tree']],
                'context':context,
                'domain': [('y_stock_quant_package_id', '=',self.id)],  
            }
    
    def unpack(self):
        rec = super(StockPackaging, self).unpack()
        records_to_delete = self.env['stock.quant.package.line'].search([('y_stock_quant_package_id', '=',self.id)])
        records_to_delete.unlink()  # Delete records       
        return rec
      
class SaleOrderKitLine(models.Model):
    _name = 'sale.order.kit.line'
    _description = 'Sale Order Kit Line'

    y_sale_stock_quant_id = fields.Many2one('stock.quant.package', string='Package', required=True, ondelete='cascade')
    y_sale_kit_id = fields.Many2one('product.template', string='Product', required=True)
    y_kit_quantity = fields.Float(string='Quantity', default=0.0)  

class StockQuant(models.Model):
    _inherit = 'stock.quant'


    y_net_weight = fields.Float(string="Net Weight")
    y_gross_weight = fields.Float(string="Gross Weight")
    y_number_of_cartons = fields.Integer(string="No of Cartons")
    y_product_packaging_id = fields.Many2one("product.packaging",string="Packaging")
    y_kit_product = fields.Char(string="Kit Product")




class StockPackagingLine(models.Model):
    _name = 'stock.quant.package.line'
    _description = 'Packaging List Line'


    y_stock_quant_package_id = fields.Many2one(
        comodel_name="stock.quant.package",
        string="Stock Quant Package"
    )
    y_stock_quant_id = fields.Many2one(
        comodel_name="stock.quant",
        string="Quant",
    )
    y_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    y_stock_quant_id_quant_ids_product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Allowed Products'
    )
    y_package_type_ids = fields.Many2many(
        comodel_name='stock.package.type',
        compute='_compute_package_type'
    )
    y_package_type_id = fields.Many2one('stock.package.type',string="Package Type")
    y_from_package = fields.Integer(string="From Package",store=True)
    y_to_package = fields.Integer(string="To Package",store=True)
    y_total_package = fields.Integer(string="Total Package",store=True)
    y_qty_in_package = fields.Float(string="Qty in Package",compute='_compute_qty_in_package',store=True)
    y_total_qty = fields.Float(string="Total Qty",compute='_compute_y_total_qty',store=True)
    y_shipping_mark = fields.Char(string="Shipping Mark")
    y_gross_weight = fields.Float(string="Gross Weight",compute='_compute_y_gross_weight',store=True)
    y_tare_weight = fields.Float(string="Tare Weight")
    y_weight_from_uom = fields.Float(string="Weight from Uom",related="y_product_id.weight",readonly=True)
    y_net_weight = fields.Float(string="Net Weight",compute='_compute_y_net_weight',store=True)


    y_length = fields.Float('Length', help="Packaging length",related="y_package_type_id.packaging_length")
    y_width = fields.Float('Width', help="Packaging Width",related="y_package_type_id.width")
    y_height = fields.Float('Height', help="Packaging Height",related="y_package_type_id.height")
    y_dimension = fields.Selection(string='Dimension',related="y_package_type_id.y_dimension")
    y_volume = fields.Float('Volume',compute='_compute_y_volume',store=True)
    y_cubic_meter = fields.Float(string="CBM",compute='_compute_cbm_calculation',store=True,digits = (12,12))

    y_kit_product = fields.Char(string="Kit Product")
    y_group = fields.Many2one('packing.list.group',string="Group")
    
    @api.onchange('y_group')
    def _check_group_dimensions(self):
        for record in self:
            if record.y_group:
                # Get all records in the model and filter them
                all_lines = self.env['stock.quant.package.line'].search([('y_stock_quant_package_id','=',record.y_stock_quant_package_id.id)])
                group_lines = all_lines.filtered(lambda line: line.y_group.id == record.y_group.id)

                print(group_lines,'group_lines')
                for line in group_lines:
                    if (line.y_length != record.y_length or
                        line.y_width != record.y_width or
                        line.y_height != record.y_height):
                        raise ValidationError(
                            "All lines within the same group must have the same dimensions (Length, Width, Height)."
                        )

   
    
    @api.depends('y_product_id')
    def _compute_y_kit_product(self):
        for rec in self:
            stock_quant_package_val = self.env['stock.quant.package'].browse(self._context.get('ref_quant_id'))
            
            if stock_quant_package_val:
                stock_quant_val = stock_quant_package_val.quant_ids.filtered(lambda x: x.product_id == rec.y_product_id)
                
                if stock_quant_val:
                    rec.y_kit_product = stock_quant_val[0].y_kit_product
                else:
                    rec.y_kit_product = False

                    
                    
                    
    @api.onchange('y_product_id')
    def _onchange_product_id(self):
        self._compute_y_kit_product()

    @api.depends('y_length','y_width','y_height')
    def _compute_y_volume(self):
        for record in self:
            if record.y_length or record.y_width or record.y_height:
                record.y_volume = record.y_length * record.y_width * record.y_height
            else:
                record.y_volume = 0.0 

    @api.depends('y_volume','y_dimension')
    def _compute_cbm_calculation(self):
        for record in self:
            if record.y_dimension == 'cm':
                record.y_cubic_meter = record.y_volume / 1000000  # Convert cm^3 to m^3
            elif record.y_dimension == 'mm':
                record.y_cubic_meter = record.y_volume / 1000000000  # Convert mm^3 to m^3
            else:
                record.y_cubic_meter = record.y_volume # Convert meter



    @api.depends('y_package_type_id')
    def _compute_y_cubic_meter(self):
        for record in self:
            if record.y_package_type_id:
                record.y_cubic_meter = record.y_package_type_id.packaging_length * record.y_package_type_id.height * record.y_package_type_id.width
            else:
                record.y_cubic_meter = 0.0 
 

    @api.onchange('y_product_id')
    def _onchange_y_product_id(self):
        for record in self:
            if record.y_product_id.packaging_ids:
                record.y_package_type_id = record.y_product_id.packaging_ids.mapped('package_type_id')[0]
            else:
                record.y_package_type_id = False


    # @api.depends('y_stock_quant_id')
    # def _compute_y_stock_quant_id_quant_ids_product_ids(self):
    #     for record in self:
    #         stock_quant_val = self.env['stock.quant.package'].browse(self._context.get('ref_quant_id'))
            
    #         if stock_quant_val:
    #             record.y_stock_quant_id_quant_ids_product_ids = stock_quant_val.quant_ids.mapped('product_id')
    #         else:
    #             record.y_stock_quant_id_quant_ids_product_ids = False

    @api.depends('y_product_id')
    def _compute_package_type(self):
        for record in self:
            if record.y_product_id:
                record.y_package_type_ids = record.y_product_id.packaging_ids.mapped('package_type_id')
            else:
                record.y_package_type_ids = False


    
        

    @api.depends('y_product_id','y_total_package','y_total_qty')
    def _compute_qty_in_package(self):
        for record in self:
            record.y_qty_in_package = 0.0 
            if record.y_product_id and record.y_total_package:
                record.y_qty_in_package = math.ceil(record.y_total_qty / record.y_total_package) if record.y_total_package < record.y_total_qty else 1.0
            else:
                record.y_qty_in_package = False


    # @api.depends('y_from_package','y_to_package')
    # def _compute_y_total_package(self):
    #     for record in self:
    #         if record.y_from_package and record.y_to_package:
    #             if record.y_from_package > record.y_to_package:
    #                 raise UserError("From Package should be less than To Package")
    #             else:
    #                 record.y_total_package = record.y_to_package - record.y_from_package + 1
    #         else:
    #             if record.y_from_package == 0:
    #                 record.y_total_package = record.y_to_package
    #             else:
    #                 record.y_total_package = 0


    @api.onchange('y_to_package')
    def _onchange_y_from_package(self):
        for record in self:
            if record.y_to_package:
                existing_package_lines = self.env['stock.quant.package.line'].search([
                ('y_product_id', '=', record.y_product_id.id),
                ('y_package_type_id', '=', record.y_package_type_id.id),
                ('y_stock_quant_package_id','=',self._context.get('ref_quant_id')),('id','!=',record._origin.id)
                ], limit=1,order='id desc')
                if existing_package_lines:
                    record.y_from_package = existing_package_lines.y_to_package + 1
            else:
                record.y_from_package = 0


    @api.depends('y_product_id')
    def _compute_y_total_qty(self):
        for rec in self:
            if self._context.get('ref_quant_id'):
                stock_quant_package_val = self.env['stock.quant.package'].browse(self._context.get('ref_quant_id'))
                stock_quant_val = stock_quant_package_val.quant_ids.filtered(lambda x: x.product_id == rec.y_product_id)
                
                if stock_quant_val:
                    rec.y_total_qty = stock_quant_val[0].quantity
                
                else:
                    rec.y_total_qty = 0.0
            else:
                rec.y_total_qty = 0.0
            


    @api.depends('y_net_weight','y_tare_weight','y_package_type_id')
    def _compute_y_gross_weight(self):
        for rec in self:
            if rec.y_net_weight and rec.y_package_type_id.base_weight or rec.y_tare_weight:
                base_weight = rec.y_package_type_id.base_weight
                all_lines = self.env['stock.quant.package.line'].search([('y_stock_quant_package_id','=',rec.y_stock_quant_package_id.id)])
                group_lines = all_lines.filtered(lambda line: line.y_group.id == rec.y_group.id)
                
                group_count = len(group_lines)

                print(group_count, rec.y_group.y_group, 'Group count and Group name')

                if group_count > 1:
                    if rec.y_total_package > 1:
                        base_weight = (base_weight / group_count) * rec.y_total_package
                    else:
                        base_weight = base_weight / group_count
                else:
                    if rec.y_total_package > 1:
                        base_weight = base_weight * rec.y_total_package
                    else:
                        base_weight = base_weight
                rec.y_gross_weight = rec.y_net_weight + base_weight + rec.y_tare_weight
                print(base_weight,'Base weight',rec.y_gross_weight)
            else:
                rec.y_gross_weight = 0.0
                
                
    
   


    @api.depends('y_gross_weight','y_total_qty')
    def _compute_y_net_weight(self):
        self.y_net_weight = 0.0 
        for rec in self:
            if rec.y_weight_from_uom and rec.y_total_qty:
                rec.y_net_weight = rec.y_weight_from_uom * rec.y_total_qty
            else:
                rec.y_net_weight = 0.0 


    def action_confirm(self):
        for rec in self:
            grouped_records = self.filtered(lambda x: x.y_product_id == rec.y_product_id)
            stock_quant_package_val = self.env['stock.quant.package'].browse(self._context.get('ref_quant_id'))
            stock_quant_vals = stock_quant_package_val.quant_ids.filtered(lambda x: x.product_id == rec.y_product_id)
            
            if stock_quant_vals:
                if len(stock_quant_vals) == 1:
                    # Single line in stock_quant_vals, sum the weights from grouped_records
                    quant = stock_quant_vals[0]
                    quant.y_gross_weight = sum(grouped_records.mapped('y_gross_weight'))
                    quant.y_net_weight = sum(grouped_records.mapped('y_net_weight'))
                    quant.y_number_of_cartons = sum(grouped_records.mapped('y_total_package'))
                else:
                    # Multiple lines in stock_quant_vals, distribute weights proportionally
                    total_qty = sum(stock_quant_vals.mapped('quantity'))
                    gross_weight_per_unit = sum(grouped_records.mapped('y_gross_weight')) / total_qty
                    net_weight_per_unit = sum(grouped_records.mapped('y_net_weight')) / total_qty
                    number_of_cartons_per_unit = sum(grouped_records.mapped('y_total_package')) / total_qty
                    
                    for quant in stock_quant_vals:
                        quant.y_gross_weight = quant.quantity * gross_weight_per_unit
                        quant.y_net_weight = quant.quantity * net_weight_per_unit
                        quant.y_number_of_cartons = quant.quantity * number_of_cartons_per_unit
            
            if stock_quant_package_val:
                stock_quant_package_val.write({'y_state': 'inprogress'})
        



class AccountMove(models.Model):
    _inherit = 'account.move'

    y_package_ids = fields.Many2many('stock.quant.package', string='Packages',store=True,domain="[('y_state', '!=', 'validated')]")

    def action_post(self):
        rec = super(AccountMove, self).action_post()
        for move in self:
            for package in move.y_package_ids:
                package.write({
                    'y_invoice_ids': [(4, move.id)],
                    'y_state': 'validated',
                    'y_invoice_date': move.invoice_date
                })
        return rec

            

  




        




