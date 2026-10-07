from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, Command, fields, models
from odoo.osv import expression
from odoo.tools import float_compare, float_round, float_is_zero, OrderedSet

class StockMove(models.Model):
    _inherit = "stock.move"

    y_btb_line_id = fields.Many2one('branch.to.branch.transfer.line')
    y_branch_to_branch_ids = fields.Many2one('branch.to.branch.transfer.line', string="Branch To Branch Transfer Line")

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        lines = super(StockMove,self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description)
        
        # STO OUT Transfer Valuation Account Entry Replace Debit Account
        if self.picking_id.y_btb_id and not self.picking_id.y_btb_picking_out_id and not self.picking_id.y_btb_picking_in_id:            
            if lines.get('debit_line_vals'):
                lines.get('debit_line_vals').update({'account_id':self.picking_id.y_btb_id.y_btb_config_id.y_intranit_account_id.id})

        # STO IN Transfer Valuation Account Entry Replace Credit Account
        if self.picking_id.y_btb_id and self.picking_id.y_btb_picking_out_id:            
            if lines.get('credit_line_vals'):
                lines.get('credit_line_vals').update({'account_id':self.picking_id.y_btb_id.y_btb_config_id.y_intranit_account_id.id})

        return lines

    def _compute_kit_quantitiessss(self, product_id, kit_qty, kit_bom, filters):
        """ Computes the quantity delivered or received when a kit is sold or purchased.
        A ratio 'qty_processed/qty_needed' is computed for each component, and the lowest one is kept
        to define the kit's quantity delivered or received.
        :param product_id: The kit itself a.k.a. the finished product
        :param kit_qty: The quantity from the order line
        :param kit_bom: The kit's BoM
        :param filters: Dict of lambda expression to define the moves to consider and the ones to ignore
        :return: The quantity delivered or received
        """
        qty_ratios = []
        kit_qty = kit_qty / kit_bom.product_qty
        boms, bom_sub_lines = kit_bom.explode(product_id, kit_qty)

        def get_qty(move):
            if move.picked:
                return move.product_uom._compute_quantity(move.quantity, move.product_id.uom_id, rounding_method='HALF-UP')
            else:
                return move.product_qty

        for bom_line, bom_line_data in bom_sub_lines:
            # skip service since we never deliver them
            if bom_line.product_id.type == 'service':
                continue
            if float_is_zero(bom_line_data['qty'], precision_rounding=bom_line.product_uom_id.rounding):
                # As BoMs allow components with 0 qty, a.k.a. optionnal components, we simply skip those
                # to avoid a division by zero.
                continue
            bom_line_moves = self.filtered(lambda m: m.bom_line_id == bom_line)
            if bom_line_moves:
                # We compute the quantities needed of each components to make one kit.
                # Then, we collect every relevant moves related to a specific component
                # to know how many are considered delivered.
                uom_qty_per_kit = bom_line_data['qty'] / (bom_line_data['original_qty'])
                qty_per_kit = bom_line.product_uom_id._compute_quantity(uom_qty_per_kit / kit_bom.product_qty, bom_line.product_id.uom_id, round=False)
                if not qty_per_kit:
                    continue
                incoming_qty = sum(bom_line_moves.filtered(filters['incoming_moves']).mapped(get_qty))
                outgoing_qty = sum(bom_line_moves.filtered(filters['outgoing_moves']).mapped(get_qty))
                # qty_processed = incoming_qty - outgoing_qty
                # qty_processed = bom_line_moves.quantity
                qty_processed = sum(bom_line_move.quantity for bom_line_move in bom_line_moves)
                # We compute a ratio to know how many kits we can produce with this quantity of that specific component
                qty_ratios.append(float_round(qty_processed / qty_per_kit, precision_rounding=bom_line.product_id.uom_id.rounding))
            else:
                return 0.0
        if qty_ratios:
            # Now that we have every ratio by components, we keep the lowest one to know how many kits we can produce
            # with the quantities delivered of each component. We use the floor division here because a 'partial kit'
            # doesn't make sense.
            return min(qty_ratios) // 1
        else:
            return 0.0


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    

    @api.constrains('qty_done')
    def _constrains_qty_done(self):
        for rec in self:
            if sum(rec.move_id.move_line_ids.mapped('qty_done')) > rec.move_id.product_uom_qty and rec.picking_id.y_btb_id:
                raise ValidationError(_('''Can not process more quantities than demand'''))

class StockPicking(models.Model):
    _inherit = "stock.picking"

    y_btb_id = fields.Many2one('branch.to.branch.transfer',string='Branch To Branch Transfer')
    y_account_move_id = fields.Many2one('account.move')
    y_btb_picking_out_id = fields.Many2one('stock.picking',string="Btb Picking Out")
    y_btb_picking_in_id = fields.Many2one('stock.picking',string="Btb Picking In")
   

    company_id = fields.Many2one(
        'res.company', string='Company', related=False,
        readonly=True, store=True, index=True,default=lambda self: self.env.company.id)     

    def _prepare_grn(self):
        stock_transfer_operation = self.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
        if not stock_transfer_operation:
            raise ValidationError(_('''Branch Transfer Operation not Available'''))
        return {
            'name' : self.y_btb_id.y_btb_config_id.y_receipt_sequence_id.next_by_id(),
            'y_btb_picking_out_id':self.id,
            'partner_id':self.y_btb_id.y_from_partner_id.id,
            'y_btb_id':self.y_btb_id.id,
            'picking_type_id':stock_transfer_operation.id,
            'origin':self.y_btb_id.y_name,
            'location_id':stock_transfer_operation.default_location_src_id.id,
            'location_dest_id':self.y_btb_id.y_btb_config_id.y_to_location_id.id,
            'company_id':self.y_btb_id.y_to_warehouse_id.company_id.id,
        }
    
    def _prepare_grn_lines(self):
        stock_transfer_operation = self.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
        if not stock_transfer_operation:
            raise ValidationError(_('''Branch Transfer Operation not Available'''))

        # analytic_distribution = False
        # account_analytic_distribution_id = self.env['account.analytic.distribution.model'].search([('warehouse_id','=',self.y_btb_id.y_to_warehouse_id.id)],limit=1)
        # if account_analytic_distribution_id:
        #     analytic_distribution = account_analytic_distribution_id.analytic_distribution

        return [(0,0,{
            'name':self.name,
            'product_id':line.product_id.id,
            'date_deadline':line.date_deadline,
            'product_uom':line.product_uom.id,
            'product_uom_qty':line.quantity,
            'location_id':stock_transfer_operation.default_location_src_id.id,
            'location_dest_id':self.y_btb_id.y_btb_config_id.y_to_location_id.id,
            # 'analytic_distribution':analytic_distribution,
            'company_id':self.y_btb_id.y_to_warehouse_id.company_id.id,
        })for line in self.move_ids_without_package]


    def button_validate(self):
        if self.y_btb_id:
            stock_transfer_operation = self.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
            if not stock_transfer_operation:
                raise ValidationError(_('''Branch Transfer Operation not Available'''))
            if self.y_btb_id:
                if self.y_btb_id.y_status == 'close':
                    raise ValidationError(_('''Can not validate transfer of a closed Branch Transfer Order'''))
                if self.y_btb_picking_out_id:
                    if self.y_btb_id.y_is_interstate and self.y_btb_picking_out_id.y_account_move_id.state != 'posted':
                        raise ValidationError(_('''Invoice to be Processed'''))

        result = super(StockPicking, self).button_validate()
        


        
        if self.y_btb_id:
            # Intra Branch Transfer Entry
            for line in self.move_ids_without_package:
                line.y_btb_line_id.y_deliv_qty = line.quantity
            if self.y_btb_id.y_btb_config_id.y_is_interstate == False:
                am_vals = []
                if not self.y_btb_id.y_branch_sale_entry_ids and self.y_btb_id and not self.y_btb_picking_out_id and not self.y_btb_picking_in_id:
                    if self.move_ids and self.move_ids.stock_valuation_layer_ids:
                        line_vals = []
                        ref = self.y_btb_id.y_name
                        am_vals = [{'ref':ref,
                                    'partner_id':self.partner_id.id,
                                    'date':fields.Date.context_today(self),
                                    'journal_id':self.y_btb_id.y_btb_config_id.y_branch_sale_journal_id.id,
                                    'y_branch_sale_btb_id':self.y_btb_id.id,
                                    'move_type': 'entry',
                                    'line_ids':[]
                                    }]

                        for line in self.move_ids:
                            svl_quantity = sum(line.stock_valuation_layer_ids.mapped('quantity'))
                            svl_value = sum(line.stock_valuation_layer_ids.mapped('value'))
                            vals = (0,0,{'ref':ref + ' - ' + line.product_id.name,
                                         'name':ref + ' - ' + line.product_id.name,
                                         'partner_id':self.partner_id.id,
                                         'product_id':line.product_id.id,
                                         'product_uom_id':line.product_uom.id,
                                         'quantity':svl_quantity,
                                         'balance':svl_value,
                                         'account_id':self.y_btb_id.y_btb_config_id.y_branch_sale_account_id.id})
                            line_vals.append(vals)

                        svl_quantity = sum(self.move_ids.stock_valuation_layer_ids.mapped('quantity'))
                        svl_value = abs(sum(self.move_ids.stock_valuation_layer_ids.mapped('value')))
                        line_vals.append((0,0,{'ref':ref,
                                               'name':ref,
                                               'partner_id':self.partner_id.id,
                                               'product_id':False,
                                               'product_uom_id':False,
                                               'quantity':svl_quantity,
                                               'balance':svl_value,
                                               'account_id':self.y_btb_id.y_btb_config_id.y_receivable_payable_offset_account_id.id}))
                        
                        am_vals[0]['line_ids'] = line_vals
                if am_vals:
                    account_moves = self.env['account.move'].sudo().create(am_vals)
                    account_moves.sudo()._post()


            # Create Landed Cost for Diffrence Amount


            
            # if self.y_btb_id and self.y_btb_picking_out_id:
            #     for move in self.move_ids:
            #         branch_out_valuation_ids = self.y_btb_picking_out_id.move_ids.filtered(lambda x:x.product_id == move.product_id).stock_valuation_layer_ids
            #         if branch_out_valuation_ids:
            #             branch_out_valuation_value = sum(branch_out_valuation_ids.mapped('value'))
            #             if abs(branch_out_valuation_value) != sum(move.stock_valuation_layer_ids.mapped('value')):
            #                 price_unit = abs(branch_out_valuation_value) - sum(move.stock_valuation_layer_ids.mapped('value'))
            #                 landed_costs = self.env['stock.landed.cost'].sudo().create({'picking_ids': [(6,0,self.ids)],
            #                                                                             'account_journal_id':self.y_btb_id.y_btb_config_id.y_branch_purchase_journal_id.id,
            #                                                                             'cost_lines': [(0, 0, {
            #                                                                             'product_id': self.y_btb_id.y_btb_config_id.y_lanaded_cost_product_id.id,
            #                                                                             'name': self.y_btb_id.y_btb_config_id.y_lanaded_cost_product_id.name,
            #                                                                             'account_id': self.y_btb_id.y_btb_config_id.y_intranit_account_id.id,
            #                                                                             'price_unit': price_unit,
            #                                                                             'split_method': 'by_quantity',
            #                                                                         })],
            #                                                                     })
                            
            #                 landed_costs.sudo().compute_landed_cost()
            #                 landed_costs.valuation_adjustment_lines.filtered(lambda x:x.product_id != move.product_id).unlink()
            #                 landed_costs.valuation_adjustment_lines.filtered(lambda x:x.product_id == move.product_id).write({'additional_landed_cost':price_unit})
            #                 landed_costs.sudo().with_company(landed_costs.company_id.id).button_validate()
            #                 landed_costs.stock_valuation_layer_ids.sudo().write({'description':"{} - {}".format(landed_costs.name,",".join(landed_costs.cost_lines.product_id.mapped('name')))})


            if self.y_btb_id.y_btb_config_id.y_is_interstate == False:
                am_vals = []
                if not self.y_btb_id.y_branch_purchase_entry_ids and self.y_btb_id and self.y_btb_picking_out_id:
                    if self.move_ids and self.move_ids.stock_valuation_layer_ids:
                        line_vals = []
                        ref = self.y_btb_id.y_name
                        am_vals = [{'ref':ref,
                                    'partner_id':self.partner_id.id,
                                    'date':fields.Date.context_today(self),
                                    'journal_id':self.y_btb_id.y_btb_config_id.y_branch_purchase_journal_id.id,
                                    'y_branch_sale_btb_id':self.y_btb_id.id,
                                    'move_type': 'entry',
                                    'line_ids':[]
                                    }]

                        for line in self.move_ids:
                            svl_quantity = sum(line.stock_valuation_layer_ids.mapped('quantity'))
                            svl_value = sum(line.stock_valuation_layer_ids.mapped('value'))
                            vals = (0,0,{'ref':ref + ' - ' + line.product_id.name,
                                         'name':ref + ' - ' + line.product_id.name,
                                         'partner_id':self.partner_id.id,
                                         'product_id':line.product_id.id,
                                         'product_uom_id':line.product_uom.id,
                                         'quantity':svl_quantity,
                                         'balance':svl_value,
                                         'account_id':self.y_btb_id.y_btb_config_id.y_branch_purchase_account_id.id})
                            line_vals.append(vals)

                        svl_quantity = sum(self.move_ids.stock_valuation_layer_ids.mapped('quantity'))
                        svl_value = -(sum(self.move_ids.stock_valuation_layer_ids.mapped('value')))
                        line_vals.append((0,0,{'ref':ref,
                                               'name':ref,
                                               'partner_id':self.partner_id.id,
                                               'product_id':False,
                                               'product_uom_id':False,
                                               'quantity':svl_quantity,
                                               'balance':svl_value,
                                               'account_id':self.y_btb_id.y_btb_config_id.y_receivable_payable_offset_account_id.id}))
                        
                        am_vals[0]['line_ids'] = line_vals
                if am_vals:
                    account_moves = self.env['account.move'].sudo().create(am_vals)
                    account_moves.sudo()._post()

            


            if result == True and self.y_btb_id and not self.y_btb_picking_out_id:
                grn = self.env['stock.picking'].sudo().create(self._prepare_grn())
                grn.sudo().write({
                            'move_ids_without_package':self._prepare_grn_lines(),
                            'scheduled_date':self.y_btb_id.y_delivery_date,
                            'company_id':self.y_btb_id.y_to_warehouse_id.company_id.id,
                            })

                self.y_btb_picking_in_id = grn.id
                grn.state = 'assigned'

                # move_lines_ids = []
                # for component in self.move_line_ids_without_package:
                    
                #     vals = ({
                #     'company_id':component.company_id.id,
                #     'lot_id':component.lot_id.id,
                #     'qty_done': component.qty_done,
                #     'product_uom_id': component.product_uom_id.id,
                #     'location_id': component.location_id.id,
                #     'location_dest_id': component.location_dest_id.id,
                #     'product_id': component.product_id.id,
                #     'picking_type_id': component.picking_type_id.id,
                #     'move_id':grn.move_ids_without_package.filtered(lambda x:x.product_id == component.product_id).id,
                #     'state':'assigned'

                #     })
                #     move_line = self.env['stock.move.line'].create(vals)
                #     move_lines_ids.append(move_line.id) 
                # grn.move_line_ids_without_package = [(6, 0, move_lines_ids)]

                move_lines_ids = []
                vals_list = []
                for component in self.move_line_ids_without_package:
                    vals = (0,0,{
                    'company_id':self.y_btb_id.y_to_warehouse_id.company_id.id,
                    'lot_id':component.lot_id.id,
                    'quantity': component.quantity,
                    'product_uom_id': component.product_uom_id.id,
                    'location_id': stock_transfer_operation.default_location_src_id.id,
                    'location_dest_id': self.y_btb_id.y_btb_config_id.y_to_location_id.id,
                    'product_id': component.product_id.id,
                    'picking_type_id': component.picking_type_id.id,
                    'state':'assigned',
                    })
                    vals_list.append(vals)
                    
                grn.move_line_ids_without_package = vals_list
        return result

    #auto placing of lot based on previous btb
    def action_confirm(self):
        result = super().action_confirm()
        if self.y_btb_picking_out_id:
            lot_list = self.y_btb_picking_out_id.move_line_ids_without_package.mapped('lot_id')
            index = 0
            for move_line_ids in self.move_line_ids_without_package:
                try:
                    move_line_ids.lot_id = lot_list[index].id
                    index += 1
                except:
                    pass
        return result