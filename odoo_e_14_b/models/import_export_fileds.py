from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo import api, fields, models, _
from num2words import num2words
from calendar import monthrange
from lxml import etree
from odoo.exceptions import UserError,ValidationError

class AccountMoveNews(models.Model):
    _inherit = "l10n_in.port.code"
    
    y_city = fields.Char(string="City")
    y_pre_carriage = fields.Selection([('bysea', 'By Sea'),('byair', 'By Air'),('byroad', 'By Road'),('byrail', 'By Rail')],string="Pre Carriage",copy=False,tracking=True)
    y_country_id = fields.Many2one('res.country',string="Country")

class AccountMoveNews(models.Model):
    _inherit = "account.move"

    y_country_orgin_goods_id = fields.Many2one('res.country',string="Country of origin",tracking=True)
    y_country_final_destination_id = fields.Many2one('res.country',string="Country of Final Destination",tracking=True)
    y_final_destination_id = fields.Many2one('res.country',string="Final Destination",tracking=True)
    y_pre_carriage = fields.Selection([('bysea', 'By Sea'),('byair', 'By Air'),('byroad', 'By Road'),('byrail', 'By Rail')],string="Pre Carriage",copy=False,tracking=True)
    y_vessel_number = fields.Char(string="Vessel/Flight No",tracking=True)
    y_port_loading_id = fields.Many2one('l10n_in.port.code',string="Port of Loading",tracking=True)
    y_port_discharge_id = fields.Many2one('l10n_in.port.code',string="Port of Discharge",tracking=True)
    y_export_type_new = fields.Selection([('normal','Normal'),('deemed','Deemed')],string='Export Type',tracking=True)
    y_voyage_no = fields.Char(string="Voyage No")    
    
    y_notify_party_id = fields.Many2one('res.partner',string="Notify Party")
    y_stock_packaging_id = fields.Many2one('packaging.list',string="Packaging Ref")
    y_net_weight = fields.Float(string="Net Weight")
    y_gross_weight = fields.Float(string="Gross Weight")
    y_container_number = fields.Char(string="Container No",tracking=True)
    y_container_seal_number = fields.Char(string="Container Seal No",tracking=True)

    @api.onchange('stock_packaging_id')
    def flow_values(self):
        for rec in self:
            if rec.y_stock_packaging_id:
                rec.y_container_number = rec.y_stock_packaging_id.y_container_number
                rec.y_container_seal_number = rec.y_stock_packaging_id.y_container_seal_number
                rec.y_net_weight = rec.y_stock_packaging_id.y_net_weight
                rec.y_gross_weight = rec.y_stock_packaging_id.y_gross_weight

    def action_post(self):
        res = super(AccountMoveNews,self).action_post()
        for rec in self:
            if rec.y_stock_packaging_id:
                rec.y_stock_packaging_id.y_invoice_ref_id = rec.id
        return res

class PurchaseOrderNews(models.Model):
    _inherit = "purchase.order"


    y_country_orgin_goods_id = fields.Many2one('res.country',string="Country of origin",tracking=True)
    y_country_final_destination_id = fields.Many2one('res.country',string="Country of Final Destination",tracking=True)
    y_final_destination_id = fields.Many2one('res.country',string="Final Destination",tracking=True)

    y_pre_carriage = fields.Selection([('bysea','By Sea'),('byair','By Air'),('byroad','By Road'),('byrail','By Rail')],string="Pre Carriage",copy=False,tracking=True)
    y_vessel_number = fields.Char(string="Vessel/Flight No",tracking=True)
    y_port_loading_id = fields.Many2one('l10n_in.port.code',string="Port of Loading",tracking=True)
    y_port_discharge_id = fields.Many2one('l10n_in.port.code',string="Port of Discharge",tracking=True)
    y_check_bool = fields.Boolean(default=False)

    @api.constrains('y_country_orgin_goods_id', 'y_country_final_destination_id','y_final_destination_id','y_port_loading_id','y_port_discharge_id')
    def check_countries(self):
        for rec in self:
            if rec.y_country_orgin_goods_id and rec.y_country_final_destination_id:
                if rec.y_country_orgin_goods_id == rec.y_country_final_destination_id:
                    raise UserError(_("Country of origin and Country of final destination can't be same"))
            if rec.y_country_orgin_goods_id and rec.y_final_destination_id:

                if rec.y_country_orgin_goods_id == rec.y_final_destination_id:
                    raise UserError(_("Country of origin and Final destination can't be same"))
            if rec.y_port_loading_id and rec.y_port_discharge_id:
                if rec.y_port_loading_id == rec.y_port_discharge_id:
                    raise UserError(_("Port of loading and Port of discharge can't be same"))

    @api.onchange('partner_id')
    def flow_partner_data(self):
        for rec in self:
            if rec.partner_id:
                rec.y_country_orgin_goods_id = rec.partner_id.y_country_orgin_goods_id.id
                rec.y_country_final_destination_id = rec.partner_id.y_country_final_destination_id.id
                rec.y_final_destination_id = rec.partner_id.y_final_destination_id.id

                rec.y_pre_carriage = rec.partner_id.y_pre_carriage
                rec.y_port_loading_id = rec.partner_id.y_port_loading_id.id
                rec.y_port_discharge_id = rec.partner_id.y_port_discharge_id.id
                if rec.partner_id.country_id != rec.company_id.country_id:
                    rec.y_check_bool = True


    def _prepare_invoice(self):
        res = super(PurchaseOrderNews,self)._prepare_invoice()
        for rec in self:
            res['y_country_orgin_goods_id'] = rec.y_country_orgin_goods_id.id
            res['y_country_final_destination_id'] = rec.y_country_final_destination_id.id
            res['y_final_destination_id'] = rec.y_final_destination_id.id
            res['y_pre_carriage'] = rec.y_pre_carriage
            res['y_vessel_number'] = rec.y_vessel_number
            res['y_port_loading_id'] = rec.y_port_loading_id.id
            res['y_port_discharge_id'] = rec.y_port_discharge_id.id          
        return res

class ResPartnerNews(models.Model):
    _inherit = "res.partner"


    y_country_orgin_goods_id = fields.Many2one('res.country',string="Country of origin",tracking=True)
    y_country_final_destination_id = fields.Many2one('res.country',string="Country of Final Destination",tracking=True)
    y_final_destination_id = fields.Many2one('res.country',string="Final Destination",tracking=True)

    y_pre_carriage = fields.Selection([('bysea','By Sea'),('byair','By Air'),('byroad','By Road'),('byrail','By Rail')],string="Pre Carriage",copy=False,tracking=True)
    y_port_loading_id = fields.Many2one('l10n_in.port.code',string="Port of Loading",tracking=True)
    y_port_discharge_id = fields.Many2one('l10n_in.port.code',string="Port of Discharge",tracking=True)

    @api.constrains('y_country_orgin_goods_id', 'y_country_final_destination_id','y_final_destination_id','y_port_loading_id','y_port_discharge_id')
    def check_countries(self):
        for rec in self:
            if rec.y_country_orgin_goods_id and rec.y_country_final_destination_id and rec.y_final_destination_id:
                if rec.y_country_orgin_goods_id == rec.y_country_final_destination_id:
                    raise UserError(_("Country of origin and Country of final destination can't be same"))

                if rec.y_country_orgin_goods_id == rec.y_final_destination_id:
                    raise UserError(_("Country of origin and Final destination can't be same"))
            if rec.y_port_loading_id and rec.y_port_discharge_id:
                if rec.y_port_loading_id == rec.y_port_discharge_id:
                    raise UserError(_("Port of loading and Port of discharge can't be same"))


class SaleorderNews(models.Model):
    _inherit = "sale.order"

    y_country_orgin_goods_id = fields.Many2one('res.country',string="Country of origin",tracking=True)
    y_country_final_destination_id = fields.Many2one('res.country',string="Country of Final Destination",tracking=True)
    y_final_destination_id = fields.Many2one('res.country',string="Final Destination",tracking=True)

    y_pre_carriage = fields.Selection([('bysea','By Sea'),('byair','By Air'),('byroad','By Road'),('byrail','By Rail')],string="Pre Carriage",copy=False,tracking=True)
    y_vessel_number = fields.Char(string="Vessel/Flight No",tracking=True)
    y_port_loading_id = fields.Many2one('l10n_in.port.code',string="Port of Loading",tracking=True)
    y_port_discharge_id = fields.Many2one('l10n_in.port.code',string="Port of Discharge",tracking=True)
    y_export_type_new = fields.Selection([('normal','Normal'),('deemed','Deemed')],string='Export Type',tracking=True)
    y_voyage_no = fields.Char(string="Voyage No") 
    y_check_bool = fields.Boolean(default=False)

    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleorderNews,self)._prepare_invoice()
        res.update({'y_voyage_no':self.y_voyage_no})
        return res

    @api.constrains('y_country_orgin_goods_id', 'y_country_final_destination_id','y_final_destination_id','y_port_loading_id','y_port_discharge_id')
    def check_countries(self):
        for rec in self:
            if rec.y_country_orgin_goods_id and rec.y_country_final_destination_id and rec.y_final_destination_id:
                if rec.y_country_orgin_goods_id == rec.y_country_final_destination_id:
                    raise UserError(_("Country of origin and Country of final destination can't be same"))

                if rec.y_country_orgin_goods_id == rec.y_final_destination_id:
                    raise UserError(_("Country of origin and Final destination can't be same"))
            if rec.y_port_loading_id and rec.y_port_discharge_id:
                if rec.y_port_loading_id == rec.y_port_discharge_id:
                    raise UserError(_("Port of loading and Port of discharge can't be same"))


    @api.onchange('partner_shipping_id')
    def flow_partner_data(self):
        for rec in self:
            if rec.partner_shipping_id:
                rec.y_country_orgin_goods_id = rec.partner_shipping_id.y_country_orgin_goods_id.id
                rec.y_country_final_destination_id = rec.partner_shipping_id.y_country_final_destination_id.id
                rec.y_final_destination_id = rec.partner_shipping_id.y_final_destination_id.id

                rec.y_pre_carriage = rec.partner_shipping_id.y_pre_carriage
                rec.y_port_loading_id = rec.partner_shipping_id.y_port_loading_id.id
                rec.y_port_discharge_id = rec.partner_shipping_id.y_port_discharge_id.id
                if rec.partner_shipping_id.country_id != rec.company_id.country_id:
                    rec.y_check_bool = True


    def _prepare_invoice(self):
        res = super(SaleorderNews,self)._prepare_invoice()
        for rec in self:
            res['y_country_orgin_goods_id']=rec.y_country_orgin_goods_id.id
            res['y_country_final_destination_id']=rec.y_country_final_destination_id.id
            res['y_final_destination_id']=rec.y_final_destination_id.id
            res['y_pre_carriage']=rec.y_pre_carriage
            res['y_vessel_number']=rec.y_vessel_number
            res['y_port_loading_id']=rec.y_port_loading_id.id
            res['y_port_discharge_id']=rec.y_port_discharge_id.id
            res['y_export_type_new']= rec.y_export_type_new
        
        return res