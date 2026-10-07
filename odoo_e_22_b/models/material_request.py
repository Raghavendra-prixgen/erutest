    # -*- coding: utf-8 -*-
    
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    y_material_request_id = fields.Many2one('material.request')
    y_material_req_boolean = fields.Boolean(default=False,compute='_compute_field_state',copy=False)
    
    
    @api.depends('state')
    def _compute_field_state(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        for rec in self:
            if rec.y_material_request_id and rec.state == 'done':
                print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
                rec.y_material_request_id.y_state = 'closed'
                rec.y_material_req_boolean = True
            
            else:
                rec.y_material_req_boolean = False
    
    
    
  

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'
    
    y_material_request_id = fields.Many2one('material.request')
    
    y_material_purchase_req_boolean = fields.Boolean(default=False,compute='_compute_field_state_purchase_request',copy=False)
    
    
    @api.depends('state')
    def _compute_field_state_purchase_request(self):
        for rec in self:
            print("-----------------------------------------------------------")
            if rec.y_material_request_id and rec.state == 'done':
                rec.y_material_request_id.y_state = 'closed'
                rec.y_material_purchase_req_boolean = True
            
            else:
                rec.y_material_purchase_req_boolean = False
                    # rec.y_material_request_id.y_state = 'closed'
    
    
    


class ResCompany(models.Model):
    _inherit = 'res.company'

    y_mr_sequence_id = fields.Many2one('ir.sequence',string="Material Request Sequence")



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    y_mr_sequence = fields.Many2one('ir.sequence',string="Material Request Sequence",readonly=False,related='company_id.y_mr_sequence_id')
    

    

class MaterialRequest(models.Model):
    _name = 'material.request'
    _inherit = ['mail.thread', 'mail.activity.mixin','analytic.mixin']
    _description = 'Material Request'
    _rec_name = 'y_name'

    y_name = fields.Char('Sequence',default=lambda self: _('New'),tracking=True)
    y_material_picking_ids = fields.One2many('stock.picking','y_material_request_id')
    y_purchase_material_ids = fields.One2many('purchase.request','y_material_request_id')
    y_picking_type_id = fields.Many2one('stock.picking.type', string="Operation Type",tracking=True)
    y_source_location_id = fields.Many2one('stock.location',tracking=True,string="Source Location")
    y_dest_location_id = fields.Many2one('stock.location',tracking=True,string="Destination Location")
    y_purchase_request_type_id = fields.Many2one('request.type',tracking=True,string="Purchase Request Type")
    y_material_request_line_ids = fields.One2many('material.request.line','y_material_request_id',tracking=True)
    y_request_material_boolean=fields.Boolean(default=False)
    y_picking_count = fields.Integer(compute="_compute_get_y_picking_count") 
    y_purchase_count = fields.Integer(compute="_compute_get_y_purchase_count")
    y_responsible_id = fields.Many2one('res.users',string="Responsible")
    # y_analytic_groupby_account_ids = fields.Many2many('account.analytic.account',compute="get_analytic_distribution",store=True)
    y_company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.company)
    y_state = fields.Selection([('draft','Draft'),('closed','Closed')], default='draft',tracking=True,string="State")
    y_material_rqt_bool = fields.Boolean(default=False,copy=False)

    # @api.depends('analytic_distribution')
    # def get_analytic_distribution(self):
    #     for rec in self:
    #         if rec.analytic_distribution:
    #             analytic_ids = []
    #             for analytic_key in rec.analytic_distribution.keys():
    #                 int_analytic_key = int(analytic_key)
    #                 analytic_ids.append(int_analytic_key)
    #             rec.y_analytic_groupby_account_ids = analytic_ids
    #         else:
    #             rec.y_analytic_groupby_account_ids = False

    @api.depends('y_material_picking_ids')
    def _compute_get_y_picking_count(self):
        for request in self:
            request.y_picking_count = len(request.y_material_picking_ids)
            
    @api.depends('y_purchase_material_ids')
    def _compute_get_y_purchase_count(self):
        for req in self:
            req.y_purchase_count = len(req.y_purchase_material_ids)

    @api.onchange('y_picking_type_id')
    def _get_default_location_y_picking_type_id(self):
        for rec in self:
            if rec.y_picking_type_id:
                rec.y_source_location_id = rec.y_picking_type_id.default_location_src_id.id
                rec.y_dest_location_id = rec.y_picking_type_id.default_location_dest_id.id
                for record in rec.y_material_request_line_ids:
                    record.y_picking_type_id = rec.y_picking_type_id.id

    @api.onchange('y_source_location_id')
    def _get_default_location_y_source_location_id(self):
        for rec in self:
            if rec.y_source_location_id:
                for record in rec.y_material_request_line_ids:
                    record.y_source_location_id = rec.y_source_location_id.id

    @api.onchange('y_dest_location_id')
    def _get_default_location_y_dest_location_id(self):
        for rec in self:
            if rec.y_dest_location_id:
                for record in rec.y_material_request_line_ids:
                    record.y_dest_location_id = rec.y_dest_location_id.id
        
    def action_mr_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['views'] = [(self.env.ref('stock.vpicktree').id, 'tree'),(self.env.ref('stock.view_picking_form').id,'form')]
        action['context'] = self.env.context
        action['domain'] = [('y_material_request_id', '=', self.id)]
        return action
    
    def action_mr_purchase(self):
        action = self.env["ir.actions.actions"]._for_xml_id("odoo_e_27_b.purchase_request_form_action")
        action['views'] = [(self.env.ref('odoo_e_27_b.view_purchase_request_tree').id, 'tree'),(self.env.ref('odoo_e_27_b.view_purchase_request_form').id,'form')]
        action['context'] = self.env.context
        action['domain'] = [('y_material_request_id', '=', self.id)]
        return action

    def close(self):
        self.y_state = 'closed'
    
    def reset(self):
        self.y_state = 'draft'
        # self.y_material_rqt_bool = False

    # def process_all(self):
    #     for rec in self:
    #         for each_line in rec.y_material_request_line_ids:
    #             each_line.write({'y_request_qty': each_line.y_planned_qty})

    @api.onchange('y_purchase_request_type_id')
    def _get_default_y_purchase_request_type_id(self):
        for rec in self:
            if rec.y_purchase_request_type_id:
                for record in rec.y_material_request_line_ids.filtered(lambda x:x.y_request_type == 'purchase'):
                    record.y_purchase_request_type_id = rec.y_purchase_request_type_id.id
            else:
                rec.y_purchase_request_type_id = False


    @api.model
    def create(self, vals):
        vals['y_request_material_boolean'] = True
        if vals.get('y_name', _('New')) == _('New'):
            company = self.env['res.company'].browse(vals['y_company_id'])
            sequence = company.y_mr_sequence_id
            if sequence:
                vals['y_name'] = sequence.next_by_id()
            else:                
                raise UserError("Material Request Sequence Not Configured {} Company".format(company.name))
        return super(MaterialRequest, self).create(vals)


    # @api.model
    # def create(self, vals):
    #     vals['y_request_material_boolean']=True
    #     sequence = self.env['ir.sequence'].browse(int(self.env['ir.config_parameter'].sudo().get_param('material_request.y_mr_sequence')))

    #     print(sequence,4444444444444444444444444444444444444)
    #     vals['y_name'] = self.env['ir.sequence'].next_by_code(sequence.code)
    #     print(vals['y_name'],33333333333333333333333333333333333333333333333)
    #     return super(MaterialRequest, self).create(vals)
    
    

    def request_material(self):
        # if all([True if line.y_request_qty == 0 else False for line in self.y_material_request_line_ids]):
        #     raise ValidationError("Quantity to ship should be greter than zero")
        for each_line in self.y_material_request_line_ids:
            each_line.write({'y_request_qty': each_line.y_planned_qty})

        moves = self.y_material_request_line_ids
        operations = []        
        for move in moves:
            operations.append((move.y_picking_type_id.id,move.y_source_location_id.id,move.y_dest_location_id.id))
        operations = set(operations)
        for mov in moves:       
            if mov.y_request_type == 'stock':
                for operation in operations:                   
                    if operation[0]:
                        picking = {
                            'y_material_request_id' : self.id,
                            'user_id' : self.y_responsible_id.id,
                            'picking_type_id' : operation[0],
                            'location_id' : operation[1],
                            'location_dest_id' : operation[2],
                            'move_ids_without_package' : [],
                            'company_id' : self.y_company_id.id,
                        }
                       
                        stock_moves = moves.filtered(lambda mov: mov.y_picking_type_id.id ==  operation[0] and mov.y_source_location_id.id == operation[1] and mov.y_dest_location_id.id == operation[2] and mov.y_request_qty )
                        for stock_move in stock_moves:
                            picking['move_ids_without_package'].append((0, 0,{
                                'product_id' : stock_move.y_product_id.id,
                                'name' : stock_move.y_product_id.partner_ref,
                                'product_uom_qty' : stock_move.y_request_qty,
                                'product_uom' : stock_move.y_product_id.uom_id.id,
                                'y_mr_line_id' : stock_move.id,
                                'location_id': operation[1],
                                'group_id':stock_move.y_group_id.id,
                                'location_dest_id' : operation[2],
                                'company_id':self.y_company_id.id,
                            }))
                            if stock_move.y_request_type != 'purchase':
                                stock_move.y_requested_qty += stock_move.y_request_qty
                                stock_move.y_request_qty = 0
                    
                        if len(stock_moves):
                            picking = self.env['stock.picking'].create(picking)
                            for move in picking.move_ids_without_package:
                                move.y_mr_line_id.y_transfer_order_ids = [(4, move.picking_id.id, 0)]
                        

            else:                
                plines = self.y_material_request_line_ids.filtered(lambda req: req.y_request_type == 'purchase')
                prequests = []
                for pline in plines:
                    y_purchase_request_type_id = pline.y_material_request_id.y_purchase_request_type_id
                    if not y_purchase_request_type_id:
                        raise ValidationError(_("Purchase Request Sequence Not Configured"))
                    else:
                        request_obj = y_purchase_request_type_id
                        purchase = {
                            'y_material_request_id' : self.id,
                            'request_type_id' : request_obj.id,
                            'name': request_obj.sequence_id.next_by_id(),
                            'line_ids' : [],
                            'approver_ids': [(6,0,request_obj.approver_ids.ids)],
                        }
                    
                        purchase_lines = plines.filtered(lambda lin:lin.y_request_qty > 0)
                        for purchase_line in purchase_lines:
                            
                            purchase['line_ids'].append((0, 0,{
                                'product_id': purchase_line.y_product_id.id,
                                'product_uom_id' : purchase_line.y_product_id.uom_id.id,
                                'product_qty' : purchase_line.y_request_qty,
                                'y_mr_line_id' : purchase_line.id,
                            }))
                            purchase_line.y_requested_qty += purchase_line.y_request_qty
                            purchase_line.y_request_qty = 0
                            
                        if len(purchase_lines) :  
                            purchase = self.env['purchase.request'].create(purchase)
                            
                            for line in purchase.line_ids:
                                line.y_mr_line_id.y_purchase_request_ids = [(4, line.request_id.id, 0)]
                                
            if self.y_material_picking_ids != False or self.y_purchase_material_ids != False:
                self.y_material_rqt_bool = True
                
            

    
    # def request_material(self):
        # for line in self.y_material_request_line_ids:
        #     line._validate_analytic_distribution()
        # for rec in self:
            # for each_line in rec.y_material_request_line_ids:
            #         each_line.write({'y_request_qty': each_line.y_planned_qty})

        
        # moves = self.y_material_request_line_ids
       
        # operations = []
        
        # for move in moves:
        #     operations.append((move.y_picking_type_id.id,move.y_source_location_id.id,move.y_dest_location_id.id))
        # operations = set(operations)
        
        # for mov in moves:       
        #     if mov.y_request_type != 'purchase':
        #         for operation in operations: 
        #             print(222222222222222222222222222222222222222222222222222222)                  
        #             if operation[0]:
        #                 print(333333333333333333333333333333333333333333333)
        #                 picking = {
        #                     'y_material_request_id' : self.id,
        #                     'user_id' : self.y_responsible_id.id,
        #                     'picking_type_id' : operation[0],
        #                     'location_id' : operation[1],
        #                     'location_dest_id' : operation[2],
        #                     'move_ids_without_package' : []
        #                 }
                       
        #                 stock_moves = moves.filtered(lambda mov: mov.y_picking_type_id.id ==  operation[0] and mov.y_source_location_id.id == operation[1] and mov.y_dest_location_id.id == operation[2] and mov.y_request_qty and not mov.y_transfer_order_ids.move_ids_without_package.filtered(lambda x:x.picking_id.picking_type_id.id ==  operation[0] and x.picking_id.location_id.id == operation[1] and x.location_dest_id.id == operation[2] and x.product_id == mov.y_product_id and x.product_uom_qty == mov.y_request_qty))
        #                 print(stock_moves,444444444444444444444444444444444444444444444)
        #                 for stock_move in stock_moves:
        #                     picking['move_ids_without_package'].append((0, 0,{
        #                         'product_id' : stock_move.y_product_id.id,
        #                         'name' : stock_move.y_product_id.partner_ref,
        #                         'product_uom_qty' : stock_move.y_request_qty,
        #                         'product_uom' : stock_move.y_product_id.uom_id.id,
        #                         'y_mr_line_id' : stock_move.id,
        #                         'location_id': operation[1],
        #                         'group_id':stock_move.y_group_id.id,
        #                         'location_dest_id' : operation[2],
        #                         # 'analytic_distribution': stock_move.analytic_distribution,
        #                     }))
        #                     if stock_move.y_request_type != 'purchase':
        #                         stock_move.y_requested_qty += stock_move.y_request_qty
        #                         stock_move.y_request_qty = 0
                    
        #                 if len(stock_moves):
        #                     picking = self.env['stock.picking'].create(picking)
        #                     for move in picking.move_ids_without_package:
        #                         move.y_mr_line_id.y_transfer_order_ids = [(4, move.picking_id.id, 0)]
                        

        #     else:                
        #         plines = self.y_material_request_line_ids.filtered(lambda req: req.y_request_type == 'purchase')
        #         prequests = []
        #         for pline in plines:
        #             y_purchase_request_type_id = pline.y_material_request_id.y_purchase_request_type_id
        #             if not y_purchase_request_type_id:
        #                 raise ValidationError(_("Purchase Request Sequence Not Configured"))
        #             else:
        #                 request_obj = y_purchase_request_type_id
        #                 purchase = {
        #                     'y_material_request_id' : self.id,
        #                     'request_type_id' : request_obj.id,
        #                     'name': request_obj.sequence_id.next_by_id(),
        #                     'line_ids' : []
        #                 }
                    
        #                 purchase_lines = plines.filtered(lambda lin:lin.y_request_qty and not lin.y_purchase_request_ids ,)
        #                 for purchase_line in purchase_lines:
                            
        #                     purchase['line_ids'].append((0, 0,{
        #                         'product_id': purchase_line.y_product_id.id,
        #                         'product_uom_id' : purchase_line.y_product_id.uom_id.id,
        #                         'product_qty' : purchase_line.y_request_qty,
        #                         'y_mr_line_id' : purchase_line.id,
        #                         # 'analytic_distribution': purchase_line.analytic_distribution,
        #                     }))
        #                     purchase_line.y_requested_qty += purchase_line.y_request_qty
        #                     purchase_line.y_request_qty = 0
                            
        #                 if len(purchase_lines) :  
        #                     purchase = self.env['purchase.request'].create(purchase)
                            
        #                     for line in purchase.line_ids:
        #                         line.y_mr_line_id.y_purchase_request_ids = [(4, line.request_id.id, 0)]

        # self.process_all()


class MaterialRequestLine(models.Model):
    _name = 'material.request.line'
    _inherit = ['analytic.mixin']
    _description = 'Material Request Line'
          
    y_company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.company)
    y_material_request_id = fields.Many2one('material.request',string="Material Request")  
    y_picking_type_id = fields.Many2one('stock.picking.type', string="Operation Type")
    y_source_location_id = fields.Many2one('stock.location',string="Source Location")
    y_dest_location_id = fields.Many2one('stock.location',string="Destination Location")
    y_purchase_request_type_id = fields.Many2one('request.type',string="Purchase Request Type")
    y_product_id = fields.Many2one('product.product',string="Product")
    y_available_qty = fields.Float(compute='_compute_available_qty', string="Available Qty")

    @api.depends('y_product_id', 'y_source_location_id', 'y_material_request_id.y_source_location_id')
    def _compute_available_qty(self):
        for rec in self:
            source_location = rec.y_source_location_id or rec.y_material_request_id.y_source_location_id
            if rec.y_product_id and source_location:
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', rec.y_product_id.id),
                    ('location_id', '=', source_location.id),
                ])
                rec.y_available_qty = sum(quant.mapped('inventory_quantity_auto_apply'))
            elif rec.y_product_id:
                rec.y_available_qty = rec.y_product_id.qty_available
            else:
                rec.y_available_qty = 0.0

    y_forcast_qty = fields.Float(related='y_product_id.virtual_available',string="Forcast Qty")
    y_planned_qty = fields.Float(string="Qty")
    y_requested_qty = fields.Float(readonly=True, string="Qty Shipped")
    y_request_qty = fields.Float(string="Qty To Ship")
    y_request_type = fields.Selection([('stock','Internal Transfer'),('purchase','Purchase Request')],default='stock',string="Request Type") 
    y_transfer_order_ids = fields.Many2many('stock.picking', readonly=True,string="Transfer Order")
    y_purchase_request_ids = fields.Many2many('purchase.request', readonly=True,string="Purchase Request")
    y_group_id = fields.Many2one('procurement.group')

    
    # @api.depends('y_product_id','y_picking_type_id','y_material_request_id.y_picking_type_id')
    # def _compute_analytic_distribution(self):
    #     for line in self:
    #         distribution = line.env['account.analytic.distribution.model']._get_distribution({
    #             "product_id": line.y_product_id.id,
    #             "company_id": line.y_company_id.id,
    #             })
    #         if line.y_material_request_id.analytic_distribution:
    #             line.analytic_distribution = line.y_material_request_id.analytic_distribution
    #         else:
    #             line.analytic_distribution = distribution or line.analytic_distribution

    # def _validate_analytic_distribution(self):
    #     for line in self:
    #         #enforce analytic validation
    #         line.with_context(validate_analytic = True)._validate_distribution(**{
    #             "product_id": line.y_product_id.id,
    #             "company_id": line.y_company_id.id,
    #         })
 
    def unlink(self):
        for each in self:
            if each.y_requested_qty:
                raise UserError(_("Request Can't be Deleted after Processing"))
        return super(MaterialRequestLine, self).unlink()

    @api.constrains('y_request_qty')
    def _check_something(self):
        for rec in self:
            print(rec.y_request_qty,11111111111111111111111111111111111111)
            print(rec.y_planned_qty,2222222222222222222222222222222222222222)
            print(rec.y_requested_qty,333333333333333333333333333333333333)
            if rec.y_request_qty > rec.y_planned_qty - rec.y_requested_qty:
                raise ValidationError(_("Keep Calm and don't process more quantity than planned"))
    
    @api.model
    def create(self, vals):
        mr = self.env['material.request'].browse(vals.get('y_material_request_id'))
        if not vals['y_picking_type_id'] and  vals['y_request_type'] == 'stock':
            vals['y_picking_type_id'] = mr.y_picking_type_id.id
        if not vals['y_source_location_id'] and  vals['y_request_type'] == 'stock':
            vals['y_source_location_id'] = mr.y_source_location_id.id
        if not vals['y_dest_location_id'] and  vals['y_request_type'] == 'stock':
            vals['y_dest_location_id'] = mr.y_dest_location_id.id
        if vals.get('y_request_type') == 'purchase':
            if not vals.get('y_purchase_request_type_id'):
                vals['y_purchase_request_type_id'] = mr.y_purchase_request_type_id.id

        return super(MaterialRequestLine, self).create(vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    y_mr_line_id = fields.Many2one('material.request.line')
    
class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'
    
    y_mr_line_id = fields.Many2one('material.request.line')
    
    
