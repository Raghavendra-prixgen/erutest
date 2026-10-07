from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import  UserError, ValidationError, AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    y_gross_amount = fields.Monetary(string='Base Amount', store=True, tracking=True,compute='_amount_y_gross_amount')
    y_service_charges = fields.Monetary(string='Charges', store=True, tracking=True,compute='_amount_y_service_charges')



    @api.depends('order_line.price_total','order_line.product_id')
    def _amount_y_gross_amount(self):
        for order in self:
            gross  = 0.0
            for line in order.order_line:
                # line._compute_amount()
                if line.product_id.type in ('product','consu'):
                    gross += line.price_subtotal
            order.update({
                'y_gross_amount': order.currency_id.round(gross),
            })

    @api.depends('order_line.price_total','order_line.product_id')
    def _amount_y_service_charges(self):
        for order in self:
            charges = 0.0
            for line in order.order_line:
                # line._compute_amount()
                if line.product_id.type =='service':
                    charges += line.price_subtotal  
            order.update({
                'y_service_charges': order.currency_id.round(charges),
            })

 
class AccountMove(models.Model):
    _inherit = 'account.move'

            
    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
         for move in self:
            for line in move.invoice_line_ids:
                orders = line.purchase_order_id
                for order in orders:
                    if order and move.invoice_date and order.date_approve and move.invoice_date < order.date_approve.date():
                        raise ValidationError(_('Bill Date Should Not Be Lesser Than Purchase Order Date'))
