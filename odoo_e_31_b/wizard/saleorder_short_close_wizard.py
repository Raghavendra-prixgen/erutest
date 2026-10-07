# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tests import Form
from odoo.exceptions import UserError, ValidationError


class SaleOrderShortCloseWizard(models.TransientModel):
    _name = "saleorder.short.close.wizard"
    _description = " "


    y_order_id = fields.Many2one('sale.order')
    y_short_close_reason = fields.Char(string='Short Close Reasons')
    y_sc_so_lines_ids = fields.Many2many('sale.order.line',string='Short Close SO Lines')

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrderShortCloseWizard,self).default_get(fields_list)
        res['y_order_id'] = self._context.get('default_order_id')
        return res
    
    
    @api.onchange('y_sc_so_lines_ids')
    def _compute_so_sale_lines(self):
        for rec in self:
            lines=self.env['sale.order.line'].search([('order_id','=',self._context.get('active_id'))])
            so_lines=lines.filtered(lambda line: line.y_is_short_close == False and line.product_uom_qty > line.qty_delivered)
            rec.y_sc_so_lines_ids = [(6,0,so_lines.ids)]

    
    def button_action_short_close(self):
        if all(not line.y_is_short_close for line in self.y_sc_so_lines_ids):
            raise UserError("short close as true before confirming.")

        order_id = self.env['sale.order'].search([('id','=',self._context.get('active_id'))])
        for reason in order_id:
            reason.y_short_close_reason = self.y_short_close_reason

        # for all lines where short close boolean is true identify the related pickings which are not in done or cancelled state
        for rec in self.y_sc_so_lines_ids:
            if rec.y_is_short_close == True and rec.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
                rec.move_ids.y_is_freeze = True
                order_id.y_is_so_short_close = True
            else:
                rec.move_ids.y_is_freeze = False
        #END

        
        # #if all moves in a picking are frozen and done qty of all move is 0 then cancel that picking
        
        can_be_cancel = True
        for rec in self.y_sc_so_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
            if rec.y_is_freeze == True and rec.quantity == 0:
                can_be_cancel = True
            else:
                can_be_cancel = False
                break
        if can_be_cancel:
            picking=self.y_sc_so_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')).picking_id
            picking.do_unreserve()        
            for rec in self.y_sc_so_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
                rec.state = 'cancel'
            
            picking.state = 'cancel'

        # #END
    
        # # #If all moves in a picking are frozen and done qty of any move is > 0 then approve the picking without creating back order
        # can_be_validate = True
        # for rec in self.y_sc_so_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
        #     if rec.y_is_freeze == True:
        #         can_be_validate = True
        #     else:
        #         can_be_validate = False
        #         break
        # if can_be_cancel == False:
        #     moves=self.y_sc_so_lines_ids.move_ids.filtered(lambda line: line.quantity > 0)
        #     if can_be_validate and moves:
        #         picking_val=self.y_sc_so_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')).picking_id
        #         for move in picking_val:
        #             res_dict = move.button_validate()
        #             if move.state != 'done':
        #                 backorder_wizard = Form(self.env['stock.backorder.confirmation'].with_context(res_dict['context'])).save()
        #                 backorder_wizard.process_cancel_backorder()


        # #END

        # #When a picking contains moves with partial done quantities and some moves are in freeze state.
        # #While validating such a picking, if user selects 'Create Backorder' then the lines in frozen state must not carry over to the backorder.

        for rec in self.y_sc_so_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
            if rec.picking_id.state not in ('done','cancel'):
                if rec.y_is_freeze == True:
                    rec._do_unreserve()
                    rec.state = 'cancel'

        # #END
