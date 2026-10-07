# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError
import pdb

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    y_is_prchase_charge = fields.Boolean("Charges",default=False,copy=False)

    def action_open_purchase_charges(self):
        order = self.env['purchase.order'].browse(self.env.context.get('order_id'))
        return order.action_open_purchase_charges()

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_open_purchase_charges(self):
        view_id = self.env.ref('odoo_e_27_b.choose_purchase_charges_view_form').id
        return {
            'name': "Add PO Charges",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.purchase.charges',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context':{'po_id':self.id}
        }

    def _create_purchase_charge_line(self,product_id ,price_unit):
        PurchaseOrderLine = self.env['purchase.order.line']
        # Apply fiscal position
        taxes = product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
        taxes_ids = taxes.ids
        if self.partner_id and self.fiscal_position_id:
            taxes_ids = self.fiscal_position_id.map_tax(taxes).ids
       
        values = {
            'order_id': self.id,
            'name': product_id.name,
            'product_uom_qty': 1,
            'product_uom': product_id.uom_id.id,
            'product_id': product_id.id,
            'price_unit': price_unit,
            'y_is_prchase_charge' : True,
            'taxes_id': [(6, 0, taxes_ids)],
        }
        
        if self.order_line:
            values['sequence'] = self.order_line[-1].sequence + 1
        pol = PurchaseOrderLine.sudo().create(values)
        return pol

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Create the landed cost line in the Tranfers 
    def button_validate(self):
        result = super(StockPicking, self).button_validate()

        current_id = self.purchase_id.order_line.filtered(lambda x :x.y_is_prchase_charge == True)
        StockLandedCost =self.env['stock.landed.cost.lines']

        if current_id and not self.landed_cost_ids and self.picking_type_id.code == 'incoming':
            for each_line in current_id:
                values = {
                    'stock_picking_id': self.id,
                    'name': each_line.product_id.name,
                    'product_id': each_line.product_id.id,
                    'price_unit': each_line.price_unit,
                    'split_method' : each_line.product_id.split_method_landed_cost,
                    }
                pol = StockLandedCost.sudo().create(values)
                pol.onchange_product_id()
                pol.price_unit = each_line.price_unit
        return result



