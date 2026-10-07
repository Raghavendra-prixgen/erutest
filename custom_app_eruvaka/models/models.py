from odoo import models, fields, api, _


class Respartner(models.Model):
    _inherit = 'res.partner'

    iec_no=fields.Char(string="IEC NO")
    iec_date=fields.Date(strimg="IEC Date")
    lut_no=fields.Char(string="LUT")
    lut_valid_till=fields.Date(string="Lut Valid Till")
    y_reg_date=fields.Date(string ="Register Date")


class Saleordercustom(models.Model):
    _inherit = 'sale.order'

    po_ref=fields.Char(string="Po Ref")
    po_date=fields.Date(string="Po Date")
    shipping_method_id = fields.Many2one('shipping.method')

class Accountmovecustom(models.Model):
    _inherit = 'account.move'

    lut_arn_nu=fields.Char(string ="LUT ARN NO")
    reg_date = fields.Date()
    valid_till=fields.Date(string ="Valid Till")
    y_export_ref_no = fields.Char(string="Export Ref No")
    y_export_ref_date = fields.Date(string="Export Date")
    e_o_e = fields.Char()
    y_note = fields.Char(string="Note")


class ResShippingMethodMenu(models.Model):
	_name = 'shipping.method'
	_description = 'Shipping Method'
	_rec_name = 'shipping_method'

	shipping_method = fields.Char(string="Shipping Method")


class Saleordercustom(models.Model):
    _inherit = 'purchase.order'

    y_notes = fields.Char(string="Notes")  

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vehicle_no = fields.Char(string="Vehicle No")
    e_waybill_no = fields.Char(string="E-waybill No")
    res_state_id = fields.Many2one('res.country.state', string="State", related='partner_id.state_id')
    nature_of_supply = fields.Selection([
        ('inter_state', 'Inter State'),
        ('intra_state', 'Intra State'),
        ],copy=False,tracking=True,string="Nature Of Supply")

