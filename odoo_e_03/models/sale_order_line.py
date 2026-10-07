from odoo import fields,models,api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    y_status = fields.Char('Document Status',store=True,compute='_compute_status_type')
    # y_currency_id = fields.Many2one('res.currency',' Currency',related="order_id.currency_id")
    y_partner_id = fields.Many2one('res.partner',' Partner',related="order_id.partner_id",store=True)
    y_remaining_qty = fields.Float("Pending Qty",compute="qty_remaining",store=True)
    y_client_order_ref = fields.Char('Customer Reference')
    y_pending_order_value = fields.Float(compute='compute_value',string='Pending Order Value',store=True)
    y_product_catag_id=fields.Many2one('product.category',related="product_id.categ_id",store=True)
    # y_open_close_so = fields.Selection([('open_so', 'OPEN SO'), ('close_so', 'CLOSE SO'), ], 'SO Status', related="order_id.open_close_mo", store=True)
    y_order_date = fields.Datetime(related="order_id.date_order", string="Order confirm Date",store=True)
    y_product_group_1 = fields.Many2one('product.group.1',string="Product Group 1")
    y_product_group_2 = fields.Many2one('product.group.2',string="Product Group 2")
    y_product_group_3 = fields.Many2one('product.group.3',string="Product Group 3")
    y_item_group = fields.Many2one('item.group')
    y_so_expected_date = fields.Datetime(related="order_id.expected_date",string=" Expected date")
    y_so_effective_date = fields.Datetime(related="order_id.effective_date",string=" Effective date")
    # y_name_ref = fields.Char(string="RFQ",related="order_id.quotation_number")
    
    @api.onchange('product_id')
    def onchange_product_id_group(self):
        for rec in self:
            if rec.product_id:
                rec.y_item_group = rec.product_id.product_tmpl_id.y_item_group.id
                rec.y_product_group_1 = rec.product_id.product_tmpl_id.y_product_group_1.id
                rec.y_product_group_2 = rec.product_id.product_tmpl_id.y_product_group_2.id
                rec.y_product_group_3 = rec.product_id.product_tmpl_id.y_product_group_3.id
                
    @api.depends('qty_delivered','product_uom_qty')
    def qty_remaining(self):
        for each in self:
            if each.product_uom_qty :
                each.y_remaining_qty = each.product_uom_qty- each.qty_delivered
            else:
                each.y_remaining_qty = 0.0

    @api.depends('y_remaining_qty','price_unit')
    def compute_value(self):
        for l in self:
            l.y_pending_order_value = l.price_unit * l.y_remaining_qty

    @api.depends('qty_delivered','qty_invoiced','product_uom_qty')
    def _compute_status_type(self):
        for line in self:
            if line.qty_delivered != line.product_uom_qty:
                line.y_status = 'Pending Order'
            if line.qty_delivered != line.qty_invoiced:
                line.y_status = 'Pending for Invoice'
            if line.state == 'cancel':
                line.y_status = 'Cancel'
            if line.qty_delivered == line.product_uom_qty == line.qty_invoiced:
                line.y_status = "Fully Invoiced"
            if line.y_is_short_close == True:
                line.y_status = "Short Close"
                
                
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def update_sol_groups(self):
        for so in self:
            for line in so.order_line:
                line.onchange_product_id_group()

