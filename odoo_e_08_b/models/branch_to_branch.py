from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import math


class BranchToBranchTransfer(models.Model):
    _name = 'branch.to.branch.transfer'
    _description = 'Branch To Branch Transfer'
    _rec_name = 'y_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    y_name = fields.Char(string='Name')
    y_btb_line_ids = fields.One2many('branch.to.branch.transfer.line','y_btb_id',copy=True,string="Branch Lines")

    y_external_document = fields.Char(string="Extrernal Document")    
    y_state = fields.Selection([
        ('approval', 'Approval Pending'),
        ('open', 'Open'),
        ('released', 'Released'),
        ('closed', 'Closed'),
        ],copy=False,index=True,tracking=True,compute='_compute_state',store=True,string="State")
    y_from_warehouse_id = fields.Many2one('stock.warehouse',string=" From Warehouse",tracking=True)
    y_to_warehouse_id = fields.Many2one('stock.warehouse',string="To Warehouse",tracking=True)
    y_from_partner_id = fields.Many2one('res.partner',string="From Address",related='y_from_warehouse_id.partner_id')
    y_to_partner_id = fields.Many2one('res.partner',string="To Address",related='y_to_warehouse_id.partner_id')
    y_dispatch_date = fields.Date('Document Date',tracking=True,copy=False)
    y_delivery_date = fields.Date('Expected Delivery Date',tracking=True,copy=False)

    y_btb_config_id = fields.Many2one('branch.to.branch.transfer.config',compute='_get_btb_config',store=True,string="B To B Config")
    y_is_interstate = fields.Boolean(related='y_btb_config_id.y_is_interstate',string='Taxable', store=True)

    y_picking_ids = fields.One2many('stock.picking','y_btb_id',string="Pickings")
    y_invoice_ids = fields.One2many('account.move', 'y_btb_id',string="Invoices")

    y_approved = fields.Boolean(string="Approved",copy=False)
    y_processed = fields.Boolean(string="Processed",copy=False)
    y_closed = fields.Boolean(string="Closed",copy=False)

    y_transfer_count = fields.Integer(compute='_get_counts',string="Transfer Count",copy=False)
    y_invoice_count = fields.Integer(compute='_get_counts',string="Invoices Count",copy=False)
    y_bill_count = fields.Integer(compute='_get_counts',string="Bills Count",copy=False)

    y_total_plan = fields.Float(compute='_compute_totals',string="Total Planed",copy=False)
    y_total_deliv = fields.Float(compute='_compute_totals',string="Total Delivered",copy=False)
    y_total_rescv = fields.Float(compute='_compute_totals',string="Total Received",copy=False)


    # y_total_plan = fields.Float(compute=False,string="Total Planed",copy=False)
    # y_total_deliv = fields.Float(compute=False,string="Total Delivered",copy=False)
    # y_total_rescv = fields.Float(compute=False,string="Total Received",copy=False)
    y_branch_sale_entry_ids = fields.One2many('account.move','y_branch_sale_btb_id',copy=False,string="Branch Sale Entry's")
    y_branch_purchase_entry_ids = fields.One2many('account.move','y_branch_purchase_btb_id',copy=False,string="Branch Purchase Entry's")

    y_status = fields.Selection([
        ('done','Complete'),
        ('delivready','Ready to Ship'),
        ('delivpart','Partially Shipped'),
        ('rescvready','Ready to Receive'),
        ('rescvpart','Paritally Received'),
        ('close','Short Closed')],compute='_compute_status',string="Status",copy=False)

    y_short_close_reason_id = fields.Many2one('barch.transfer.short.close.reason',string="Short Close Reason",copy=False)

    @api.depends('y_btb_line_ids','y_btb_line_ids.y_quantity','y_btb_line_ids.y_deliv_qty','y_btb_line_ids.y_rescv_qty')
    def _compute_totals(self):
        for rec in self:

            rec.y_total_plan = sum(rec.y_btb_line_ids.mapped('y_quantity'))
            rec.y_total_deliv = sum(rec.y_btb_line_ids.mapped('y_deliv_qty'))
            rec.y_total_rescv = sum(rec.y_btb_line_ids.mapped('y_rescv_qty'))
    
    @api.depends('y_total_plan','y_total_deliv','y_total_rescv')
    def _compute_status(self):
        for rec in self:
            if rec.y_closed != True:
                if rec.y_total_deliv == 0:
                    rec.y_status = 'delivready'
                elif rec.y_total_rescv == 0:
                    rec.y_status = 'rescvready'
                elif rec.y_total_deliv < rec.y_total_plan:
                    rec.y_status = 'delivpart'
                elif rec.y_total_rescv < rec.y_total_deliv:
                    rec.y_status = 'rescvpart'
                else:
                    rec.y_status = 'done'
            elif rec.y_total_deliv == rec.y_total_rescv == rec.y_total_plan:
                rec.y_status = 'done'
            else:
                rec.y_status = 'close'

    @api.constrains('y_dispatch_date','y_delivery_date')
    def _check_dates(self):
        for rec in self:
            if rec.y_dispatch_date < fields.date.today():
                raise ValidationError(_('''Can not create a backdated BTB'''))
            if rec.y_delivery_date < rec.y_dispatch_date:
                raise ValidationError(_('''Can not set delivery date before document date'''))
            for line in rec.y_btb_line_ids:
                if line.y_deadline and (line.y_deadline > rec.y_delivery_date or line.y_deadline < rec.y_dispatch_date):
                    raise ValidationError(_('''Product delivery deadline must be between document date and delivery date'''))

    @api.depends('y_invoice_ids')
    def _get_counts(self):
        invoices = self.env['account.move']
        for rec in self:
            rec.y_transfer_count = len(rec.y_picking_ids)
            rec.y_invoice_count = len(invoices.search([('y_btb_id', '=', self.id),('move_type','in',('out_invoice','out_refund'))]))
            rec.y_bill_count = len(invoices.search([('y_btb_id', '=', self.id),('move_type','in',('in_invoice','in_refund'))]))

    @api.depends('y_from_warehouse_id','y_to_warehouse_id')
    def _get_btb_config(self):
        for rec in self:
            rec.y_btb_config_id = False
            if rec.y_from_warehouse_id and rec.y_to_warehouse_id:
                btb_config_ids = self.env['branch.to.branch.transfer.config'].search([('y_from_warehouse_id','=',rec.y_from_warehouse_id.id),('y_to_warehouse_id','=',rec.y_to_warehouse_id.id)])
                if btb_config_ids:
                    rec.y_btb_config_id = btb_config_ids.id
                else:
                    raise ValidationError(_('''Branch To Branch Transfer has not been configured for the selected Warehouses'''))    
    
    @api.depends('y_btb_config_id','y_approved','y_processed','y_closed')
    def _compute_state(self):
        for rec in self:
            if not rec.y_approved and not rec.y_processed:
                rec.y_state = 'open'
            elif rec.y_processed and not rec.y_closed:
                rec.y_state = 'released'
            elif rec.y_closed:
                rec.y_state = 'closed'
                rec.y_picking_ids.filtered(lambda x:x.state != 'done').action_cancel()
                rec.y_invoice_ids.filtered(lambda y:y.state != 'posted').button_cancel()
            else:
                rec.y_state = 'open'

    @api.model
    def create(self, vals):
        vals.update({'y_name': self.env['ir.sequence'].next_by_code('branch.branch.transfer')})
        if not vals.get('y_btb_line_ids'):
            raise ValidationError(_('''Can not create Branch To Branch Transfer without any products'''))
        return super(BranchToBranchTransfer, self).create(vals)

    def _prepare_dc(self):
        stock_transfer_operation = self.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
        if not stock_transfer_operation:
            raise ValidationError(_('''Branch Transfer Operation not Available'''))
        return {
            'name' : self.y_btb_config_id.y_shipment_sequence_id.next_by_id(),
            'partner_id':self.y_to_partner_id.id,
            'y_btb_id':self.id,
            'picking_type_id':stock_transfer_operation.id,
            'origin':self.y_name,
            'location_id':self.y_btb_config_id.y_from_location_id.id,
            'location_dest_id':stock_transfer_operation.default_location_dest_id.id,
            'company_id':self.y_from_warehouse_id.company_id.id,
        }

    def _prepare_dc_lines(self):
        stock_transfer_operation = self.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
        if not stock_transfer_operation:
            raise ValidationError(_('''Branch Transfer Operation not Available'''))

        # analytic_distribution = False
        # account_analytic_distribution_id = self.env['account.analytic.distribution.model'].search([('warehouse_id','=',self.y_from_warehouse_id.id)],limit=1)
        # if account_analytic_distribution_id:
        #     analytic_distribution = account_analytic_distribution_id.analytic_distribution

        move_lines = []
        for line in self.y_btb_line_ids:
            if line.y_product_id.product_tmpl_id.bom_ids and line.y_product_id.product_tmpl_id.bom_ids[0].type=='phantom':
                bom = line.y_product_id.product_tmpl_id.bom_ids[0]  
                for component in bom.bom_line_ids:
                    move_lines.append((0, 0, {
                        'name': '{}:{}'.format(self.y_name, component.product_id.name),
                        'product_id': component.product_id.id,
                        'y_btb_line_id': line.id,
                        'date_deadline': line.y_deadline,
                        'product_uom': component.product_uom_id.id,
                        'product_uom_qty': component.product_qty * line.y_quantity, 
                        'quantity': component.product_qty * line.y_quantity,  
                        'location_id': self.y_btb_config_id.y_from_location_id.id,
                        'location_dest_id': stock_transfer_operation.default_location_dest_id.id,
                        'company_id': self.sudo().y_from_warehouse_id.company_id.id,
                        'bom_line_id':component.id
                    }))
            else:
                # Regular product, keep existing functionality
                move_lines.append((0, 0, {
                    'name': '{}:{}'.format(self.y_name, line.y_product_id.name),
                    'product_id': line.y_product_id.id,
                    'y_btb_line_id': line.id,
                    'date_deadline': line.y_deadline,
                    'product_uom': line.y_uom_id.id,
                    'product_uom_qty': line.y_quantity,
                    'quantity': line.y_quantity,
                    'location_id': self.y_btb_config_id.y_from_location_id.id,
                    'location_dest_id': stock_transfer_operation.default_location_dest_id.id,
                    'company_id': self.sudo().y_from_warehouse_id.company_id.id,
                }))
        
        return move_lines




    def process_btb(self):
        if not self.y_btb_line_ids:
            raise UserError(_("""No Products to process"""))        
        dc = self.env['stock.picking'].sudo().create(self._prepare_dc())        
        dc.sudo().write({
            'move_ids_without_package':self._prepare_dc_lines(),
            'scheduled_date':self.y_dispatch_date,
            'company_id':self.sudo().y_from_warehouse_id.company_id.id,
            })
        # dc.state = 'assigned'
        self.y_processed = True
    
    def action_close(self):
        if self.y_total_deliv == self.y_total_rescv == self.y_total_plan:
            self.y_closed = True
        else:
            return {
                'name': _('Short Close Reason'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'barch.transfer.short.close',
                'target': 'new',
                'res_id': self.env['barch.transfer.short.close'].create({'y_btb_id':self.id}).id,
                'context': self.env.context
            }

    def action_btb_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['views'] = [
            (self.env.ref('stock.vpicktree').id, 'tree'),(self.env.ref('stock.view_picking_form').id,'form')
        ]
        action['context'] = self.env.context
        action['domain'] = [('y_btb_id', '=', self.id)]
        return action
    
    def action_btb_inv(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['views'] = [
            (self.env.ref('account.view_invoice_tree').id, 'tree'),(self.env.ref('account.view_move_form').id,'form')
        ]
        action['context'] = self.env.context
        action['domain'] = [('y_btb_id', '=', self.id),('move_type','in',('out_invoice','out_refund'))]
        return action
    
    def action_btb_bill(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['views'] = [
            (self.env.ref('account.view_invoice_tree').id, 'tree'),(self.env.ref('account.view_move_form').id,'form')
        ]
        action['context'] = self.env.context
        action['domain'] = [('y_btb_id', '=', self.id),('move_type','in',('in_invoice','in_refund'))]
        return action
    
    def unlink(self):
        if self.state in ('closed','released'):
            raise ValidationError(_('''Released Branch To Branch Transfer cannot be Deleted'''.format(self.y_state)))
        return super(BranchToBranchTransfer, self).unlink()

    def check(self):
        for rec in self:
            for order_line in rec.y_btb_line_ids:
                order_line.y_deliv_qty = 0.0

                # if order_line.qty_delivered_method == 'stock_move':
                boms = order_line.y_stock_move_ids.filtered(lambda m: m.state != 'cancel').mapped('bom_line_id.bom_id')
                dropship = any(m._is_dropshipped() for m in order_line.y_stock_move_ids)
                #     # We fetch the BoMs of type kits linked to the order_line,
                #     # the we keep only the one related to the finished produst.
                #     # This bom should be the only one since bom_line_id was written on the moves

                relevant_bom = boms.filtered(lambda b: b.type == 'phantom' and
                            (b.product_id == order_line.y_product_id or
                            (b.product_tmpl_id == order_line.y_product_id.product_tmpl_id and not b.product_id)))
                if not relevant_bom:
                    relevant_bom = boms._bom_find(order_line.y_product_id, company_id=order_line.y_company_id.id, bom_type='phantom')[order_line.y_product_id]


                if relevant_bom:
                    # not written on a move coming from a PO: all moves (to customer) must be done
                    # and the returns must be delivered back to the customer
                    # FIXME: if the components of a kit have different suppliers, multiple PO
                    # are generated. If one PO is confirmed and all the others are in draft, receiving
                    # the products for this PO will set the qty_delivered. We might need to check the
                    # state of all PO as well... but sale_mrp doesn't depend on purchase.
                    if dropship:
                        moves = order_line.y_stock_move_ids.filtered(lambda m: m.state != 'cancel')
                        if any((m.location_dest_id.usage == 'customer' and m.state != 'done')
                                or (m.location_dest_id.usage != 'customer'
                                and m.state == 'done'
                                and float_compare(m.quantity,
                                                    sum(sub_m.product_uom._compute_quantity(sub_m.quantity, m.product_uom) for sub_m in m.returned_move_ids if sub_m.state == 'done'),
                                                    precision_rounding=m.product_uom.rounding) > 0)
                                for m in moves) or not moves:
                            order_line.y_deliv_qty = 0
                        else:
                            order_line.y_deliv_qty = order_line.product_uom_qty
                        continue
                    moves = order_line.y_stock_move_ids.filtered(lambda m: m.state == 'done' and not m.scrapped)
                    filters = {
                        'incoming_moves': lambda m: m.location_dest_id.usage == 'customer' and (not m.origin_returned_move_id or (m.origin_returned_move_id and m.to_refund)),
                        'outgoing_moves': lambda m: m.location_dest_id.usage != 'customer' and m.to_refund
                    }
                    order_qty = order_line.y_uom_id._compute_quantity(order_line.y_quantity, relevant_bom.product_uom_id)
                    y_deliv_qty = moves._compute_kit_quantitiessss(order_line.y_product_id, order_qty, relevant_bom, filters)
                    order_line.y_deliv_qty += relevant_bom.product_uom_id._compute_quantity(y_deliv_qty, order_line.y_uom_id)



                elif boms:
                    # if the move is ingoing, the product **sold** has delivered qty 0
                    if all(m.state == 'done' and m.location_dest_id.usage == 'customer' for m in order_line.y_stock_move_ids):
                        order_line.y_deliv_qty = order_line.y_deliv_qty
                    else:
                        order_line.y_deliv_qty = 0.0




                # stock_transfer_operation = rec.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
                # rec.y_deliv_qty = sum(rec.y_btb_id.y_picking_ids.filtered(lambda pik : pik.y_btb_picking_in_id and pik.state == 'done' and pik.picking_type_id.id in stock_transfer_operation.ids).mapped('move_ids_without_package').filtered(lambda mov : mov.product_id.id == rec.y_product_id.id).mapped('quantity'))
                order_line.y_rescv_qty = sum(order_line.y_btb_id.y_picking_ids.filtered(lambda pik : pik.y_btb_picking_out_id and pik.state == 'done' and pik.picking_type_id.id in stock_transfer_operation.ids).mapped('move_ids_without_package').filtered(lambda mov : mov.product_id.id == order_line.y_product_id.id).mapped('quantity'))





class BranchToBranchTransferLine(models.Model):
    _name = 'branch.to.branch.transfer.line'
    _description = 'Branch To Branch Transfer Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    y_btb_id = fields.Many2one('branch.to.branch.transfer',string='Branch To Branch Transfer Order')
    y_product_id = fields.Many2one('product.product', string='Product',tracking=True)
    y_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    y_quantity = fields.Float('Planned Quantity',tracking=True)
    y_deliv_qty = fields.Float('Delivered Quantity',compute='_compute_delivreciev_qty')
    y_rescv_qty = fields.Float('Received Quantity',compute='_compute_delivreciev_qty')
    y_deadline = fields.Date(string="Deadline")
    y_stock_move_ids = fields.One2many('stock.move', 'y_btb_line_id',string='Stock Move')
    y_company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id)


    @api.constrains('y_deadline')
    def _check_dates(self):
        for rec in self:
            if rec.y_deadline and (rec.y_deadline > rec.y_btb_id.y_delivery_date or rec.y_deadline < rec.y_btb_id.y_dispatch_date):
                raise ValidationError(_('''Product delivery deadline must be between document date and delivery date'''))

    @api.onchange('y_product_id')
    def set_uom_on_product(self):
        self.y_uom_id = self.y_product_id.uom_id.id
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('y_product_id'):
                raise ValidationError(_('Can not create transfer without a product'))
            if not vals.get('y_quantity'):
                raise ValidationError(_('Can not create transfer without quantity'))
        return super(BranchToBranchTransferLine, self).create(vals_list)




    @api.depends('y_btb_id','y_btb_id.y_picking_ids','y_btb_id.y_picking_ids.move_ids_without_package','y_btb_id.y_picking_ids.move_ids_without_package.quantity','y_stock_move_ids')
    def _compute_delivreciev_qty(self):
        for order_line in self:
            order_line.y_deliv_qty = 0.0
            if order_line.y_product_id.bom_ids and order_line.y_product_id.bom_ids[0].type=='phantom':



                # if order_line.qty_delivered_method == 'stock_move':
                boms = order_line.y_stock_move_ids.filtered(lambda m: m.state != 'cancel').mapped('bom_line_id.bom_id')
                dropship = any(m._is_dropshipped() for m in order_line.y_stock_move_ids)
                #     # We fetch the BoMs of type kits linked to the order_line,
                #     # the we keep only the one related to the finished produst.
                #     # This bom should be the only one since bom_line_id was written on the moves
                relevant_bom = boms.filtered(lambda b: b.type == 'phantom' and
                            (b.product_id == order_line.y_product_id or
                            (b.product_tmpl_id == order_line.y_product_id.product_tmpl_id and not b.product_id)))
                if not relevant_bom:
                    relevant_bom = boms._bom_find(order_line.y_product_id, company_id=order_line.y_company_id.id, bom_type='phantom')[order_line.y_product_id]
                if relevant_bom:
                    # not written on a move coming from a PO: all moves (to customer) must be done
                    # and the returns must be delivered back to the customer
                    # FIXME: if the components of a kit have different suppliers, multiple PO
                    # are generated. If one PO is confirmed and all the others are in draft, receiving
                    # the products for this PO will set the qty_delivered. We might need to check the
                    # state of all PO as well... but sale_mrp doesn't depend on purchase.
                    if dropship:
                        moves = order_line.y_stock_move_ids.filtered(lambda m: m.state != 'cancel')
                        if any((m.location_dest_id.usage == 'customer' and m.state != 'done')
                                or (m.location_dest_id.usage != 'customer'
                                and m.state == 'done'
                                and float_compare(m.quantity,
                                                    sum(sub_m.product_uom._compute_quantity(sub_m.quantity, m.product_uom) for sub_m in m.returned_move_ids if sub_m.state == 'done'),
                                                    precision_rounding=m.product_uom.rounding) > 0)
                                for m in moves) or not moves:
                            order_line.y_deliv_qty = 0
                        else:
                            order_line.y_deliv_qty = order_line.product_uom_qty
                        continue
                    moves = order_line.y_stock_move_ids.filtered(lambda m: m.state == 'done' and not m.scrapped)
                    filters = {
                        'incoming_moves': lambda m: m.location_dest_id.usage == 'customer' and (not m.origin_returned_move_id or (m.origin_returned_move_id and m.to_refund)),
                        'outgoing_moves': lambda m: m.location_dest_id.usage != 'customer' and m.to_refund
                    }
                    order_qty = order_line.y_uom_id._compute_quantity(order_line.y_quantity, relevant_bom.product_uom_id)
                    y_deliv_qty = moves._compute_kit_quantitiessss(order_line.y_product_id, order_qty, relevant_bom, filters)
                    order_line.y_deliv_qty += relevant_bom.product_uom_id._compute_quantity(y_deliv_qty, order_line.y_uom_id)


                elif boms:
                    # if the move is ingoing, the product **sold** has delivered qty 0
                    if all(m.state == 'done' and m.location_dest_id.usage == 'customer' for m in order_line.y_stock_move_ids):
                        order_line.y_deliv_qty = order_line.y_deliv_qty
                    else:
                        order_line.y_deliv_qty = 0.0



                stock_transfer_operation = order_line.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
                # rec.y_deliv_qty = sum(rec.y_btb_id.y_picking_ids.filtered(lambda pik : pik.y_btb_picking_in_id and pik.state == 'done' and pik.picking_type_id.id in stock_transfer_operation.ids).mapped('move_ids_without_package').filtered(lambda mov : mov.product_id.id == rec.y_product_id.id).mapped('quantity'))
                order_line.y_rescv_qty = sum(order_line.y_btb_id.y_picking_ids.filtered(lambda pik : pik.y_btb_picking_out_id and pik.state == 'done' and pik.picking_type_id.id in stock_transfer_operation.ids).mapped('move_ids_without_package').filtered(lambda mov : mov.product_id.id == order_line.y_product_id.id).mapped('quantity'))

            else:
                stock_transfer_operation = order_line.env['stock.picking.type'].search([('y_is_branch_to_branch_operation','=',True)])
                order_line.y_deliv_qty = sum(order_line.y_btb_id.y_picking_ids.filtered(lambda pik : pik.y_btb_picking_in_id and pik.state == 'done' and pik.picking_type_id.id in stock_transfer_operation.ids).mapped('move_ids_without_package').filtered(lambda mov : mov.product_id.id == order_line.y_product_id.id).mapped('quantity'))
                order_line.y_rescv_qty = sum(order_line.y_btb_id.y_picking_ids.filtered(lambda pik : pik.y_btb_picking_out_id and pik.state == 'done' and pik.picking_type_id.id in stock_transfer_operation.ids).mapped('move_ids_without_package').filtered(lambda mov : mov.product_id.id == order_line.y_product_id.id).mapped('quantity'))


