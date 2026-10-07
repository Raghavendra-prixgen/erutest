# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"

    def action_generate_serial(self):
        lot_id = self.env['stock.lot'].create({
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'name': self.env['stock.lot']._get_next_serial(self.company_id, self.product_id) or self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        })
       
        for component in self:
            vals = ({
                    'company_id':component.company_id.id,
                    'lot_id':lot_id.id,
                    'lot_name':lot_id.name,
                    'product_uom_id': component.product_uom.id,
                    'location_id': component.location_id.id,
                    'location_dest_id': component.location_dest_id.id,
                    'product_id': component.product_id.id,
                    'picking_type_id': component.picking_type_id.id,
                    'move_id':self.id,
                    'picking_id':self.picking_id.id
                    })
            move_line = self.env['stock.move.line'].create(vals)
        return self.action_show_details()    