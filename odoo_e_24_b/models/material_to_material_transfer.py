# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    y_material_to_material_transfer_id = fields.Many2one('material.to.material.transfer',copy=False)

class MaterialToMaterialTransfer(models.Model):
    _name = 'material.to.material.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin','analytic.mixin']
    _description = 'Material To Material Transfer'

    y_name = fields.Char(string="Name")
    y_effective_date = fields.Datetime(string="Effective Date",copy=False)
    y_state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            
        ],
        default='draft',
        string="State",
        copy=False,tracking=True
    )
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id)
    y_picking_ids = fields.Many2many('stock.picking',string="Picking Id")
    y_picking_count = fields.Integer(compute="get_picking_count",string="Picking Count")
    y_material_to_material_transfer_from_line_ids = fields.One2many('material.to.material.transfer.from.line','y_material_to_material_from_transfer_id',string="Material To Material Transfer From",copy=False)
    y_material_to_material_transfer_to_line_ids = fields.One2many('material.to.material.transfer.to.line','y_material_to_material_to_transfer_id',string=" Material To Material Transfer To",copy=False)


    @api.depends('y_picking_ids')
    def get_picking_count(self):
        for rec in self:
            rec.y_picking_count = len(rec.y_picking_ids.ids)

    @api.model
    def create(self, vals):
        if vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('material.to.material.transfer') or _('New')
            result = super(MaterialToMaterialTransfer, self).create(vals)
            return result

    def view_picking_values_tree(self):
        return {
            'name': ("Pickings"),
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [('y_material_to_material_transfer_id', '=', self.id)],
            'view_mode': 'tree,form'
            }

    def action_confirm(self):
        operation_type = self.env['stock.picking.type'].search([('y_material_to_material_transfer','=',True)],limit=1)
        from_location = self.y_material_to_material_transfer_from_line_ids.mapped('y_source_location_id')
        to_location = self.y_material_to_material_transfer_to_line_ids.mapped('y_destination_location_id')        
        stock_material_from_picking_obj = False
        if self.y_material_to_material_transfer_from_line_ids:
            stock_material_from_picking_obj = self.env['stock.picking'].with_context(is_material_to_material=True).create({
                'picking_type_id':operation_type.id,
                'location_id':from_location.id,
                'location_dest_id': operation_type.default_location_dest_id.id,
                'company_id':self.y_company_id.id
                
            })
            move_lines =[]
            stock_move = []
            product_val = []
            for component in self.y_material_to_material_transfer_from_line_ids:
                if component.y_product_id not in product_val:
                    vals = ({
                    'name':component.y_product_id.name,
                    'company_id':component.y_company_id.id,
                    'product_uom_qty': sum(self.y_material_to_material_transfer_from_line_ids.filtered(lambda x:x.product_id == component.y_product_id).mapped('y_product_qty')),
                    'date':fields.Datetime.now(),
                    'product_uom': component.y_product_uom_id.id,
                    'location_id': component.y_source_location_id.id,
                    'location_dest_id': operation_type.default_location_dest_id.id,
                    'product_id': component.y_product_id.id,
                    'picking_type_id': operation_type.id,
                    'analytic_distribution': self.analytic_distribution
                    })
                    move_line = self.env['stock.move'].create(vals)
                    product_val.append(component.y_product_id)
                    move_lines.append(move_line.id)
                    stock_move.append(move_line)


            move_lines_ids =[]
            for component in self.y_material_to_material_transfer_from_line_ids:
                
                vals = ({
                'company_id':component.y_company_id.id,
                'lot_id':component.y_lot_id.id,
                'qty_done': component.y_product_qty,
                'product_uom_id': component.y_product_uom_id.id,
                'location_id': component.y_source_location_id.id,
                'location_dest_id': operation_type.default_location_dest_id.id,
                'product_id': component.y_product_id.id,
                'picking_type_id': operation_type.id,
                'move_id':list(filter(lambda x:x.product_id == component.y_product_id,stock_move))[0].id,
                'state':'assigned'
                })
                move_line = self.env['stock.move.line'].create(vals)
                move_lines_ids.append(move_line.id)  

            stock_material_from_picking_obj.move_ids_without_package = [(6, 0, move_lines)]

            stock_material_from_picking_obj.move_line_ids_without_package = [(6, 0, move_lines_ids)]

            stock_material_from_picking_obj.state = 'assigned'
            stock_material_from_picking_obj.y_material_to_material_transfer_id = self.id

            self.y_picking_ids = [(4, stock_material_from_picking_obj.id)]
        if self.y_material_to_material_transfer_to_line_ids:
            stock_material_to_picking_obj_lines = self.env['stock.picking'].with_context(is_material_to_material=True).create({
                'picking_type_id':operation_type.id,
                'location_id':operation_type.default_location_src_id.id,
                'location_dest_id': to_location.id,
                'company_id':self.y_company_id.id,
                
            })
            move_lines =[]
            product_val = []
            stock_move = []

            for component in self.y_material_to_material_transfer_to_line_ids:
                if component.y_product_id not in product_val:
                    vals = ({
                    'name':component.y_product_id.name,
                    'company_id':component.y_company_id.id,
                    'product_uom_qty': sum(self.y_material_to_material_transfer_to_line_ids.filtered(lambda x:x.product_id == component.y_product_id).mapped('y_product_qty')),

                    'date':fields.Datetime.now(),
                    'product_uom': component.y_product_uom_id.id,
                    'location_id': operation_type.default_location_src_id.id,
                    'location_dest_id': component.y_destination_location_id.id,
                    'product_id': component.y_product_id.id,
                    'picking_type_id': operation_type.id,
                    'analytic_distribution': self.analytic_distribution

                    })
                    move_line = self.env['stock.move'].create(vals)
                    product_val.append(component.y_product_id)
                    stock_move.append(move_line)

                    move_lines.append(move_line.id)  

            move_lines_ids =[]
            for component in self.y_material_to_material_transfer_to_line_ids:
                vals = ({
                'company_id':component.y_company_id.id,
                'lot_id':component.y_lot_id.id,
                'qty_done': component.y_product_qty,
                'product_uom_id': component.y_product_uom_id.id,
                'location_id': operation_type.default_location_src_id.id,
                'location_dest_id': component.y_destination_location_id.id,
                'product_id': component.y_product_id.id,
                'picking_type_id': operation_type.id,
                'move_id':list(filter(lambda x:x.product_id == component.y_product_id,stock_move))[0].id,
                'state':'assigned'


                })
                move_line = self.env['stock.move.line'].create(vals)
                move_lines_ids.append(move_line.id)   
            stock_material_to_picking_obj_lines.move_ids_without_package = [(6, 0, move_lines)]
            stock_material_to_picking_obj_lines.move_line_ids_without_package = [(6, 0, move_lines_ids)]
            stock_material_to_picking_obj_lines.state = 'assigned'
            stock_material_to_picking_obj_lines.y_material_to_material_transfer_id = self.id
            self.y_picking_ids = [(4, stock_material_to_picking_obj_lines.id)]

            # stock_material_to_picking_obj.action_confirm()
            stock_material_to_picking_obj_lines.action_set_quantities_to_reservation()
            stock_material_to_picking_obj_lines.button_validate()
        if stock_material_from_picking_obj:
            # stock_material_from_picking_obj.action_confirm()
            stock_material_from_picking_obj.action_set_quantities_to_reservation()
            stock_material_from_picking_obj.button_validate()

        self.state = 'posted'


        

class MaterialToMaterialTransferFromLine(models.Model):
    _name = "material.to.material.transfer.from.line"
    _description = 'Material To Material Transfer From  Line'

    y_product_id = fields.Many2one('product.product',string="Product")
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id)

    y_product_qty = fields.Float(string="Quantity")
    y_source_location_id = fields.Many2one('stock.location',string="Source Location")
    y_product_uom_id = fields.Many2one('uom.uom',string="UOM")
    y_onhand_qty = fields.Float(string="On Hand Qty")
    y_lot_id = fields.Many2one('stock.lot',string="Lot Id")
    y_material_to_material_from_transfer_id = fields.Many2one('material.to.material.transfer',string="Material To Material From Transfer Id")

    @api.onchange('y_product_id','y_source_location_id','y_lot_id')
    def get_on_hand_qty(self):
        for rec in self:
            if rec.y_product_id:
                rec.y_product_uom_id = rec.y_product_id.uom_id.id
            if rec.y_product_id and rec.y_source_location_id and rec.y_lot_id :
                stock_quant_obj = self.env['stock.quant'].search([('product_id','=',rec.y_product_id.id),('location_id','=',rec.y_source_location_id.id),('lot_id','=',rec.y_lot_id.id)])
                rec.y_onhand_qty = stock_quant_obj.quantity



class MaterialToMaterialTransferToLine(models.Model):
    _name = "material.to.material.transfer.to.line"
    _description = 'Material To Material Transfer To  Line'

    y_product_id = fields.Many2one('product.product',string="Product")
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id)

    y_product_qty = fields.Float(string="Quantity")
    y_destination_location_id = fields.Many2one('stock.location',string="Destination Location")
    y_product_uom_id = fields.Many2one('uom.uom',string="UOM")
    y_onhand_qty = fields.Float(string="On Hand Qty")
    y_lot_id = fields.Many2one('stock.lot',string="Lot Id")
    y_material_to_material_to_transfer_id = fields.Many2one('material.to.material.transfer',string="Material To Material To Transfer")



    @api.onchange('y_product_id','y_lot_id')
    def get_on_hand_qty(self):
        for rec in self:
            if rec.y_product_id:
                rec.y_product_uom_id = rec.y_product_id.uom_id.id

            if rec.y_product_id and rec.y_lot_id:
                stock_quant_obj = self.env['stock.quant'].search([('product_id','=',rec.y_product_id.id),('location_id','=',rec.y_destination_location_id.id),('lot_id','=',rec.y_lot_id.id)])
                rec.y_onhand_qty = stock_quant_obj.quantity

class OperationType(models.Model):
    _inherit = "stock.picking.type"

    y_material_to_material_transfer = fields.Boolean()




    
    



