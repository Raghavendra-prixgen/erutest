from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MaterialRequest(models.Model):
    _inherit = 'material.request'

    y_mrp_ids = fields.Many2many('mrp.production', string="Manufacturing Orders",tracking=True)

    @api.onchange('y_mrp_ids')
    def _get_lines_from_mrp(self):
        self.y_material_request_line_ids = [(2, line.id, 0) for line in self.y_material_request_line_ids.filtered(lambda req: req.y_source_id.id != False)]+\
            [(0, 0, {
                'y_product_id' : mrp_line.product_id.id,
                'y_planned_qty' : mrp_line.product_uom_qty - mrp_line.quantity,
                'y_source_id' : mrp_line.raw_material_production_id.id,
                'y_group_id':mrp_line.group_id.id,
                # 'analytic_distribution': mrp_line.raw_material_production_id.analytic_distribution
            }) for mrp_line in self.y_mrp_ids.mapped('move_raw_ids').filtered(lambda move: move.quantity != move.product_uom_qty)]
    

class MaterialRequestLine(models.Model):
    _inherit = 'material.request.line'

    y_source_id = fields.Many2one('mrp.production', string="Source id")
    y_source = fields.Many2one('mrp.production',compute='_get_src', string="Source")

    @api.depends('y_source_id')
    def _get_src(self):
        for rec in self:
            rec.y_source = rec.y_source_id.id


class MrpMaterialRequest(models.Model):
    _inherit = 'mrp.production'

    def mrp_materal_request_action(self):
        mr_ids = self.filtered(lambda mr:mr.state in ('confirmed','to_close','progress'))
        for rec in mr_ids.move_raw_ids:
            if rec.product_uom_qty != rec.forecast_availability:
                mr_lines = self.env['material.request.line']
                mr_lines = [(0, 0, {
                    'y_product_id' : mrp_line.product_id.id,
                    'y_planned_qty' : mrp_line.product_uom_qty - mrp_line.quantity,
                    'y_source_id' : mrp_line.raw_material_production_id.id,
                    'y_picking_type_id' : False,
                    'y_source_location_id' : False,
                    'y_dest_location_id' : False,
                    'y_request_type' : 'stock',
                    # 'analytic_distribution': mrp_line.raw_material_production_id.analytic_distribution,
                }) for mrp_line in mr_ids.mapped('move_raw_ids').filtered(lambda move: move.quantity != move.product_uom_qty)]
            
                mr_id = self.env['material.request'].create({
                    'y_mrp_ids':[(6, 0, mr_ids.ids)],
                    'y_material_request_line_ids' : mr_lines,

                    })