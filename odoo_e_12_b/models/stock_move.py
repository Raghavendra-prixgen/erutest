from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import datetime

# class StockMoveLineInherit(models.Model):
#     _inherit = "stock.move"


#     def write(self, vals):
#         res = super(StockMoveLineInherit, self).write(vals)
#         for rec in self:
#             if rec.move_line_nosuggest_ids and rec.picking_type_id.use_create_lots:
#                 for line in rec.move_line_nosuggest_ids:
#                     if not line.lot_name:
#                         line.lot_name = """{}/{}""".format(rec.picking_type_id.warehouse_id.code,self.env['ir.sequence'].next_by_code(rec.picking_type_id.custom_sequence.code))
#         return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.quantity, precision_digits=precision_digits) for move_line in self.move_line_ids_without_package.filtered(lambda m: m.state not in ('done', 'cancel')))
        lines_to_check = self.move_line_ids_without_package
        if not no_quantities_done:
            lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.quantity, 0, precision_rounding=line.product_uom_id.rounding))
        for l in lines_to_check:
            if l.product_id.tracking == 'lot' and self.picking_type_id.use_create_lots == True:
                if not l.lot_name and not l.lot_id:
                    l.lot_id=self.env['stock.lot'].create({'name':self.env['ir.sequence'].next_by_code(l.picking_type_id.y_custom_sequence.code),
                    'product_id':l.product_id.id,'company_id':l.company_id.id,'y_vendor':l.picking_id.partner_id.id}).id
        for line in lines_to_check:
            if line.product_id.tracking == 'serial' and self.picking_type_id.use_create_lots == True:
                if not line.lot_name and not line.lot_id:
                    line.lot_id=self.env['stock.lot'].create({'name':self.env['ir.sequence'].next_by_code(line.picking_type_id.y_sn_sequence.code),
                    'product_id':line.product_id.id,'company_id':line.company_id.id,'y_vendor':line.picking_id.partner_id.id}).id

        return super(StockPicking, self).button_validate()

# """{}/{}/{}""".format(l.picking_type_id.warehouse_id.code,datetime.now().date(),