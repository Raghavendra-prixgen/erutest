from urllib import request
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import json
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

# class WorkCentreCategory(models.Model):
#     _name = 'workcenter.category'

#     name = fields.Char(string='Name')
#     categ_sequence_id = fields.Many2one('ir.sequence',string='Sequence')
#     active = fields.Boolean(default=True)
#     company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company.id, index=1)
    
    # @api.constrains('name','company_id')
    # def check_item_group_code(self):
    #     for rec in self:
    #         docs=rec.env['workcenter.category'].search([('name','=',rec.name),('company_id','=',rec.company_id.id)])
    #         if len(docs) > 1:
    #             raise ValidationError(_("""Name already exists!"""))


class WorkCenter(models.Model):
    _inherit ='mrp.workcenter'

    # workcentre_category_id = fields.Many2one('workcenter.category',string='Work Center Category') 
    # is_workcenter_category_id = fields.Boolean(default=False)

    # @api.model_create_multi
    # def create(self,vals_list):
    #     for values in vals_list:
    #         sequence = self.env['workcenter.category'].browse(values.get('workcentre_category_id')).categ_sequence_id
    #         if values.get('workcentre_category_id') or (values.get('code') == False and sequence):
    #             values.update({'code':sequence.next_by_id()})
    #     res=super().create(vals_list)
    #     return res

    


    # def write(self, values):
    #     res =super(WorkCenter, self).write(values)
    #     if values.get('workcentre_category_id') or (not self.code and self.workcentre_category_id.categ_sequence_id):
    #         self.code = self.workcentre_category_id.categ_sequence_id.next_by_id() 
    #     return res

    # @api.onchange('workcentre_category_id')
    # def _onchange_workcentre_category_id(self):
    #     for rec in self:
    #         if rec.code:
    #             rec.is_workcenter_category_id = True
    #         else:
    #             rec.is_workcenter_category_id = False


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    y_output_quantity = fields.Float(string="Output Quantity", store=True)
    y_output_bool = fields.Boolean(string="Output Boolean")

    
class workOrderCategory(models.Model):
    _name = 'wizard.outquantity'

    y_output_quantity = fields.Float(string="Quantity Output", required=True)
    y_workorder_id = fields.Many2one('mrp.workorder')
    y_po_demand = fields.Float(related='y_workorder_id.y_total_workorder_demand')
    y_po_total_output_qty = fields.Float(related='y_workorder_id.y_total_output_quantity')
    y_po_remaining_qty = fields.Float(related='y_workorder_id.y_total_workorder_remaining')
    y_is_done_workorder = fields.Boolean()

    @api.onchange('y_output_quantity')
    def _onchange_output_quantity(self):
        if self.y_is_done_workorder == True and self.y_output_quantity < self.y_po_remaining_qty:
            return {
                    'warning': {'title': _('User Warning'), 'message': _('Output Quantity is less than remaining quantity press ok to continue'),},
                    }

        if self.y_is_done_workorder == True and self.y_output_quantity > self.y_po_remaining_qty:
            return {
                    'warning': {'title': _('User Warning'), 'message': _('Output Quantity is more than remaining quantity'),},
                    }


    @api.onchange('y_workorder_id')
    def _onchange_workorder_id(self):
        for rec in self:
            rec.y_workorder_id = self.env['mrp.workorder'].browse(self._context.get('workorder_id'))
           

    def added(self):
        timeline_obj = self.env['mrp.workcenter.productivity']
        # domain = [('workorder_id', '=', self._context.get('active_id')), ('y_output_bool', '=', False)]
        domain = [('y_workorder_id', '=', self._context.get('active_id'))]
        

        wod=self.env['mrp.workorder'].search([('id','=',self._context.get('active_id'))])

        if (self.y_output_quantity + wod.y_total_output_quantity) > wod.y_total_workorder_demand:
           
            raise UserError("Output quantity should not be greater than product quantity")


        total_output_quantity_list = wod.production_id.workorder_ids.filtered(lambda x: x.y_workcenter_routing_sequence < wod.y_workcenter_routing_sequence and x.state != 'cancel').mapped('y_total_output_quantity')
        if len(total_output_quantity_list):
            for line in total_output_quantity_list: 
                if (wod.y_total_output_quantity + self.y_output_quantity) > line:
                    raise UserError("Output quantity should not be greater than product quantity")
        

        productivity_workorder = self.env['mrp.workcenter.productivity'].search(domain)
        if productivity_workorder:
            productivity_workorder[0].y_output_quantity = self.y_output_quantity
            # productivity_workorder[0].y_output_bool = True
            if sum(wod.time_ids.mapped('y_output_quantity')) > wod.y_total_workorder_demand:
                raise UserError("Output quantity should not be greater than product quantity")
            

       
        if wod.production_id.workorder_ids[-1] == wod:
            wod.production_id.qty_producing = sum(wod.time_ids.mapped('y_output_quantity'))

        if self.y_is_done_workorder == True:
            self.y_workorder_id.y_total_workorder_remaining = 0
            self.y_workorder_id.with_context(y_is_done_workorder=True).button_finish()
       
        # if wod.production_id.workorder_ids[-1] != wod and wod.production_id.qty_producing == wod.y_total_output_quantity:
        
        # Disabling Auto Mark As Done
        # if wod.y_total_workorder_demand == wod.y_total_output_quantity:
        #     if self.env.user.has_group('manufacturing_base_17.group_mo_user_validation_workorder'):
        #         if wod.production_id.workorder_ids[-1] != wod:
        #             wod.do_finish()
        #         else:
        #             wod.action_open_manufacturing_order()
        #             wod.production_id.button_mark_done()
        #     else:
        #         wod.do_finish()

        


        
        # if self.env.user.has_group('manufacturing_base_17.group_mo_user_validation_workorder')

        # for timeline in timeline_obj.search(domain):
        #   timeline.y_output_quantity = self.y_output_quantity
        #   timeline.y_output_bool = True 
        # wod.production_id.qty_producing = wod.y_total_output_quantity
            
        return True


    

class workOrderCategory(models.Model):
    _inherit = 'mrp.workorder'

    y_total_output_quantity = fields.Float(string = "Total output quantity",  compute ='compute_total_outquantity' )
    y_workcenter_routing_sequence = fields.Integer(string = "Workcenter Routing Sequence", related = "operation_id.sequence", store = True)
    y_total_workorder_demand = fields.Float(string="Demand",compute="get_total_wordorder_demand")
    y_total_workorder_remaining = fields.Float(string="Remaining",compute="compute_total_remaining_quantity")


    #this is for validation is like without start of previous workorder its next workorder should not started
    def button_start(self):
        if self.env['ir.config_parameter'].sudo().get_param('odoo_e_19_b.sequential_operation'):
            workorder_obj = self.production_id.workorder_ids.filtered(lambda x:x.state != 'cancel').ids
            if workorder_obj.index(self.id) != 0:
                previous_workorder_index = workorder_obj.index(self.id) - 1
                previous_workorder = workorder_obj[previous_workorder_index]
                previous_workorder_obj = self.env['mrp.workorder'].browse(previous_workorder)
                if previous_workorder_obj.date_planned_finished:
                    if previous_workorder_obj.y_total_output_quantity == 0:
                        raise UserError("{} Operation Output Quantity not Recored".format(previous_workorder_obj.name))
                else:
                    raise UserError('Previous operation {} is not yet started'.format(previous_workorder_obj.operation_id.name))


        #reserved_availability field not in odoo 17 ....................................................... 

        if self.env['ir.config_parameter'].sudo().get_param('odoo_e_19_b.y_restrict_reserved_qty_warning'):
            product_ids = self.production_id.move_raw_ids.filtered(lambda x:x.quantity < 1 and x.product_uom_qty > 0).product_id.mapped('name')
            product_names = "\n".join(product_ids)
            if self.production_id.bom_id.ready_to_produce == 'all_available' and any(self.production_id.move_raw_ids.filtered(lambda x:x.quantity <= 0 and x.product_uom_qty > 0)):
                raise ValidationError("Below products are not reserved to start the production\n{}".format(product_names))
            
            if self.production_id.bom_id.ready_to_produce == 'asap' and self.production_id.move_raw_ids[:1].quantity <= 0 and self.production_id.move_raw_ids[:1].product_uom_qty > 0:
                raise ValidationError("{} is not reserved to start the production".format(self.production_id.move_raw_ids[:1].product_id.name))

        #reserved_availability field not in odoo 17 ....................................................... 

        res = super().button_start()
        for rec in self:
            if self.production_id.workorder_ids[-1] == rec and rec.y_total_output_quantity > 0:
                self.production_id.qty_producing = rec.y_total_output_quantity

        return res

    @api.depends('production_id')
    def get_total_wordorder_demand(self):
        for rec in self:
            if rec:
                rec.y_total_workorder_demand = rec.production_id.product_qty
            else:
                rec.y_total_workorder_demand = 0

    @api.depends('y_total_output_quantity','y_total_workorder_demand')
    def compute_total_remaining_quantity(self):
        for line_record in self:
            if line_record:
                line_record.y_total_workorder_remaining = line_record.y_total_workorder_demand-line_record.y_total_output_quantity

    # @api.depends('time_ids.output_quantity')
    # def compute_total_outquantity(self):
    #     for rec in self:
    #         if rec:
    #             mrp_obj = list(self)[-1:][0]
    #             rec.y_total_output_quantity = sum(rec.time_ids.mapped('output_quantity'))
    #             print(rec.y_total_output_quantity,111111111111111111111111111111111111111111111)
    #             print(rec.production_id.product_qty,222222222222222222222222222222222222222222222222)
    #             if mrp_obj.y_total_output_quantity > rec.production_id.product_qty:
                    
    #                 raise UserError("Output quantity should not be greater than product quantity1")

    @api.depends('time_ids.y_output_quantity')
    def compute_total_outquantity(self):
        for rec in self:
            if rec:
                rec.y_total_output_quantity = sum(rec.time_ids.mapped('y_output_quantity'))
                # if rec.y_total_output_quantity > rec.total_workorder_demand:
                #     raise UserError("Output quantity should not be greater than product quantity1")
            

    def button_pending(self):
        res = super(workOrderCategory, self).button_pending()
        return {
                    'name':_("Workorder_wizard"),
                    'view_mode': 'form',
                    'view_id': self.env.ref('odoo_e_19_b.mrp_workorder_center_category_ZZZZ').id,
                    'view_type': 'form',
                    'res_model': 'wizard.outquantity',
                    'context':{'y_workorder_id': self.id},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'active_ids':self.ids
                }

    def button_finish(self):
        for rec in self:
            if rec.y_total_workorder_remaining > 0 and not rec._context.get('y_is_done_workorder'):
                context = dict(default_workorder_id=rec.id,default_y_is_done_workorder=True,default_output_quantity=rec.y_total_workorder_remaining)
                context.update({'y_workorder_id': rec.id})
                return {
                        'name':_("Workorder_wizard"),
                        'view_mode': 'form',
                        'view_id': rec.env.ref('odoo_e_19_b.mrp_workorder_center_category_ZZZZ').id,
                        'view_type': 'form',
                        'res_model': 'wizard.outquantity',
                        'context':context,
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'active_ids':rec.ids
                    }
            else:
                return super(workOrderCategory, self).button_finish()

    def unlink(self):
        for rec in self:
            if rec.date_start or rec.state == 'done':
                raise UserError("Operation cannot be Deleted")
        res = super(workOrderCategory,self).unlink()
        return res

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    y_remove_consumption_warning = fields.Boolean(string="Disable Consumption Warning")
    y_restrict_reserved_qty_warning = fields.Boolean(string="Allow operations Based on material Availability")
    y_sequential_operation  = fields.Boolean(string="Sequential Operation")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            y_remove_consumption_warning = bool(params.get_param('odoo_e_19_b.y_remove_consumption_warning')) or False,
            y_restrict_reserved_qty_warning = bool(params.get_param('odoo_e_19_b.y_restrict_reserved_qty_warning')) or False,
            y_sequential_operation = bool(params.get_param('odoo_e_19_b.y_sequential_operation')) or False,

        )
        return res

    def set_values(self):
        super(ResConfigSettings,self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('odoo_e_19_b.y_remove_consumption_warning',self.y_remove_consumption_warning)
        self.env['ir.config_parameter'].sudo().set_param('odoo_e_19_b.y_restrict_reserved_qty_warning',self.y_restrict_reserved_qty_warning)
        self.env['ir.config_parameter'].sudo().set_param('odoo_e_19_b.y_sequential_operation',self.y_sequential_operation)

class MrpProductionOutputQty(models.Model):
    _inherit = 'mrp.production'

    mrp_production_child_count = fields.Integer(copy=False)

    y_so_origin = fields.Char("Sale Order.")
    y_partner_shipping_id = fields.Many2one('res.partner',string="Customer")
    # so_origin = fields.Char("Parent Source")

    def action_confirm(self):
        res = super(MrpProductionOutputQty,self).action_confirm()
        for rec in self:
            for line in rec.workorder_ids:
                line.y_total_workorder_demand = rec.product_qty
        return res

    def button_mark_done(self):
        for rec in self.workorder_ids.filtered(lambda x:x.state != 'cancel'):
            if rec.date_planned_finished:
                if rec.y_total_output_quantity == 0:
                    raise UserError("{} Operation Output Quantity not Recored".format(rec.name))
            else:
                raise UserError("{} Operation Not Started".format(rec.name))
        return super(MrpProductionOutputQty, self).button_mark_done()




    #this is standard function,Display the warning based on Boolean is configuraation
    # def _pre_button_mark_done(self):
    #     productions_to_immediate = self._check_immediate()
    #     if productions_to_immediate:
    #         return productions_to_immediate._action_generate_immediate_wizard()

    #     for production in self:
    #         if float_is_zero(production.qty_producing, precision_rounding=production.product_uom_id.rounding):
    #             raise UserError(_('The quantity to produce must be positive!'))
    #         if production.move_raw_ids and not any(production.move_raw_ids.mapped('quantity')):
    #             raise UserError(_("You must indicate a non-zero amount consumed for at least one of your components"))

    #     consumption_issues = self._get_consumption_issues()
    #     if not self.env['ir.config_parameter'].sudo().get_param('manufacturing_base_17.y_remove_consumption_warning'):
    #         if consumption_issues:
    #             return self._action_generate_consumption_wizard(consumption_issues)

    #     quantity_issues = self._get_quantity_produced_issues()
    #     if quantity_issues:
    #         return self._action_generate_backorder_wizard(quantity_issues)
    #     return True


    # def action_check_availibility(self):
    #     for rec in self:
    #         rec.action_assign()



    # @api.depends('y_so_origin','origin')
    # def _compute_partner_shipping_origin(self):
    #     for rec in self:
    #         parent_sale_obj = self.env['sale.order'].search([('name','=',rec.y_so_origin)])
    #         if parent_sale_obj:
    #             rec.y_partner_shipping_id = parent_sale_obj.partner_shipping_id.id
    #         else:
    #             parent_sale = self.env['sale.order'].search([('name','=',rec.origin)])
    #             if not parent_sale:
    #                 mrp_origin = self.env['mrp.production'].search([('name','=',rec.origin)])
    #                 sale_origin = self.env['sale.order'].search([('name','=',mrp_origin.origin)])
    #                 if sale_origin:
    #                     rec.y_partner_shipping_id = sale_origin.partner_shipping_id.id
    #                 else:
    #                     if mrp_origin:
    #                         sale_origin = self.env['sale.order'].search([('name','=',mrp_origin.y_so_origin)])
    #                         rec.y_partner_shipping_id = sale_origin.partner_shipping_id.id
    #             else:
    #                 sale_origin = self.env['sale.order'].search([('name','=',rec.origin)])
    #                 rec.y_partner_shipping_id = sale_origin.partner_shipping_id.id


    # @api.model
    # def create(self,vals):
    #     if not vals.get('bom_id') and not self._context.get('is_co_product'):
    #         product = self.env['product.product'].browse(vals.get('product_id'))
    #         raise UserError("[{}]{} does not have BOM".format(product.default_code,product.name))

    #     return super(MrpProductionOutputQty,self).create(vals)

    
    # @api.depends('origin','name')
    # def _compute_sale_origin(self):
    #     for rec in self:
    #         parent_sale = self.env['sale.order'].search([('name','=',rec.origin)])
    #         if not parent_sale:
    #             mrp_origin = self.env['mrp.production'].search([('name','=',rec.origin)])
    #             sale_origin = self.env['sale.order'].search([('name','=',mrp_origin.origin)])
    #             if sale_origin:
    #                 rec.y_so_origin = mrp_origin.origin
    #             else:
    #                 if mrp_origin:
    #                     rec.y_so_origin = mrp_origin.y_so_origin
    #         else:
    #             rec.y_so_origin = rec.origin                
    
    def update_sale_order_number(self):
        if self.user_has_groups('odoo_e_19_b.group_mo_update_sale_order'):
            for rec in self:
                parent_sale = self.env['sale.order'].search([('name','=',rec.origin)])
                if not parent_sale:
                    mrp_origin = self.env['mrp.production'].search([('name','=',rec.origin)])
                    sale_origin = self.env['sale.order'].search([('name','=',mrp_origin.origin)])
                    if sale_origin:
                        rec.y_so_origin = mrp_origin.origin
                        rec.y_partner_shipping_id = sale_origin.partner_shipping_id.id
                    else:
                        rec.y_so_origin = mrp_origin.y_so_origin
                        sale_origin = self.env['sale.order'].search([('name','=',mrp_origin.y_so_origin)])
                        rec.y_partner_shipping_id = sale_origin.partner_shipping_id.id
                else:
                    rec.y_so_origin = rec.origin
                    sale_origin = self.env['sale.order'].search([('name','=',rec.origin)])
                    rec.y_partner_shipping_id = sale_origin.partner_shipping_id.id

                stock_picking_val = self.env['stock.picking'].search([('name','=',rec.origin)])
                if stock_picking_val:
                    rec.y_so_origin = stock_picking_val.y_so_origin
                    sale_origin = self.env['sale.order'].search([('name','=',stock_picking_val.y_so_origin)])
                    rec.y_partner_shipping_id = sale_origin.partner_shipping_id.id
        else:
            raise UserError(_("You are Not Authorised To Update Sale Order"))



    # @api.model_create_multi
    # def create(self,vals):
    #     if not self._context.get('params'):
    #         for rec in vals:       
    #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #             if sale_origin.origin:
    #                 rec['origin'] = sale_origin.origin

    #     # else:
    #     #     if self._context.get('params').get('model') != 'mrp.production' :
    #     #         for rec in vals:       
    #     #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #     #             if sale_origin.origin:
    #     #                 rec['origin'] = sale_origin.origin

    #     res = super(MrpProductionOutputQty,self).create(vals)
    #     return res

    # @api.model_create_multi
    # def create(self,vals):
    #     if not self._context.get('params'):
    #         for rec in vals:       
    #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #             if sale_origin.origin:
    #                 rec['origin'] = sale_origin.origin

    #     # else:
    #     #     if self._context.get('params').get('model') != 'mrp.production' :
    #     #         for rec in vals:       
    #     #             sale_origin = self.env['mrp.production'].search([('name','=',rec.get('origin'))])
    #     #             if sale_origin.origin:
    #     #                 rec['origin'] = sale_origin.origin

    #     res = super(MrpProductionOutputQty,self).create(vals)
    #     return res