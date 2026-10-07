# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.tests import Form
from odoo.exceptions import UserError, ValidationError


class PurchaseRegisterReportWizard(models.TransientModel):
    _name = "purchase.short.close.wizard"
    _description = " "

    y_short_close_reason = fields.Char(string='Short Close Reasons')
    y_sc_po_lines_ids = fields.Many2many('purchase.order.line',string='Short Close Purchase Order Lines')
    y_purchase_id = fields.Many2one('purchase.order')
    
    

    @api.onchange('y_purchase_id')
    def _onchange_so_po_lines(self):
        for rec in self:
            po_lines = []
            if self._context.get('default_sc_po_lines_ids'):
                po_lines = [(6,0,self._context.get('default_sc_po_lines_ids'))]
            else:
                lines = self.env['purchase.order.line'].search([('order_id','=',self._context.get('active_ids'))])
                po_line = lines.filtered(lambda line: line.y_is_short_close == False and line.product_qty != line.qty_received)
                if po_lines:
                    po_lines = [(6,0,po_line.ids)]
            rec.y_sc_po_lines_ids = po_lines
    

 
    def button_action_short_close(self):
        # import pdb; 
        # pdb.set_trace()
        if all(not line.y_is_short_close for line in self.y_sc_po_lines_ids):
            raise UserError(_("short close as true before confirming."))  

        order_id = self.env['purchase.order'].search([('id','=',self._context.get('active_id'))])
        for reason in order_id:
            reason.y_short_close_reason = self.y_short_close_reason

        # for all lines where short close boolean is true identify the related pickings which are not in done or cancelled state
        for rec in self.y_sc_po_lines_ids:
            if rec.y_is_short_close == True and rec.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
                rec.move_ids.y_is_freeze = True
                order_id.y_is_po_short_close = True
            else:
                rec.move_ids.y_is_freeze = False
        #END

        
        #if all moves in a picking are frozen and done qty of all move is 0 then cancel that picking
        
        can_be_cancel = True
        for rec in self.y_sc_po_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
            if rec.y_is_freeze == True and rec.quantity == 0:
                can_be_cancel = True
            else:
                can_be_cancel = False
                break
        if can_be_cancel:
            picking=self.y_sc_po_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')).picking_id
            for rec in self.y_sc_po_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
                rec.state = 'cancel'

        #END
    
        # #If all moves in a picking are frozen and qty of any move is > 0 then approve the picking without creating back order
        # can_be_validate = True
        # for rec in self.y_sc_po_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
        #     if rec.y_is_freeze == True:
        #         can_be_validate = True
        #     else:
        #         can_be_validate = False
        #         break

        # if can_be_cancel == False:
        #     moves=self.y_sc_po_lines_ids.move_ids.filtered(lambda line: line.quantity > 0)
        #     if can_be_validate and moves:
        #         picking_val=self.y_sc_po_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')).picking_id
        #         for move in picking_val:
        #             res_dict = move.button_validate()
        #             if move.state != 'done':
        #                 backorder_wizard = Form(self.env['stock.backorder.confirmation'].with_context(res_dict['context'])).save()
        #                 backorder_wizard.process_cancel_backorder()


        #END

        #When a picking contains moves with partial done quantities and some moves are in freeze state.
        #While validating such a picking, if user selects 'Create Backorder' then the lines in frozen state must not carry over to the backorder.

        for rec in self.y_sc_po_lines_ids.move_ids.filtered(lambda move: move.state not in ('done','cancel')):
            if rec.picking_id.state not in ('done','cancel'):
                if rec.y_is_freeze == True:
                    rec._do_unreserve()
                    rec.state = 'cancel'
                  
        #END

        
