from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MrpProductionInherit(models.Model):
    _inherit = "mrp.production"

    y_lot_boolean = fields.Boolean()

    @api.model
    def create(self, vals):

        res=super(MrpProductionInherit, self).create(vals)
        res.y_lot_boolean =True
        return res

    def action_generate_serial(self):
        self.ensure_one()
        if self.picking_type_id.y_custom_sequence and self.product_id.tracking == 'lot' and self.y_lot_boolean==True:
            self.y_lot_boolean=False

            self.lot_producing_id = self.env['stock.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name':self.env['ir.sequence'].next_by_code(self.picking_type_id.y_custom_sequence.code),
            })
        elif not self.picking_type_id.y_custom_sequence and not self.product_id.tracking == 'lot' and self.y_lot_boolean==True:
           self.y_lot_boolean=False

           self.lot_producing_id = self.env['stock.lot'].create({
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'name': self.env['stock.lot']._get_next_serial(self.company_id, self.product_id) or self.env['ir.sequence'].next_by_code('stock.lot.serial'),
            }) 
        if self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids:

            self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids.lot_id = self.lot_producing_id
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()

    # def _pre_button_mark_done(self):
    #     print(44444444444444444444444444444444444444444444444444444444444444444444)

    #     res = super(MrpProductionInherit, self)._pre_button_mark_done()
    #     self.action_generate_serial()
    #     return res

# class MrpImmediateProductionInherit(models.TransientModel):
#     _inherit = 'mrp.immediate.production'

#     def process(self):
#         res = super(MrpImmediateProductionInherit, self).process()
#         # productions_to_validate = 
#         self.env['mrp.production'].action_generate_serial(res)
#         return res
