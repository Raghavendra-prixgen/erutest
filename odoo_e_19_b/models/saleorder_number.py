from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleorderNumber(models.Model):
    _inherit = 'mrp.workorder'
    
    y_so_order_id = fields.Many2one("sale.order", string = "Sale Order", compute ="get_sale_order",store=True)
    y_customer_id = fields.Many2one("res.partner", string = "Customer", compute ="get_sale_order",store=True)

    @api.depends('production_id.y_so_origin')
    def get_sale_order(self):
        for each in self:
            each.y_so_order_id = False 
            each.y_customer_id = False
            if each.production_id:
                self.env.cr.execute("""SELECT sale.id,partner_shipping.id from sale_order sale LEFT JOIN res_partner partner_shipping on partner_shipping.id = sale.partner_shipping_id WHERE sale.name = '{}'""".format(each.production_id.y_so_origin))
                order_number = self._cr.fetchone()
                if order_number:
                    each.y_so_order_id = order_number[:1]
                    each.y_customer_id = order_number[1:2]

class StockPickingNew(models.Model):
    _inherit = "stock.picking"

    y_so_origin = fields.Char(string="Sale Order")

    @api.model
    def create(self,vals):
        res = super(StockPickingNew,self).create(vals)
        if res.purchase_id:
            res.y_so_origin = res.purchase_id.y_so_origin
            stock_val = self.env['stock.picking'].search([('name','=',res.origin)])
            if stock_val:
                res.y_so_origin = stock_val.y_so_origin
        return res

    # def update_sale_order(self):
    #     if self.user_has_groups('manufacturing_base_17.group_mo_update_sale_order'):
    #         for rec in self:
    #             if rec.origin:
    #                 mrp_val = self.env['mrp.production'].search([('name','=',rec.origin)])
    #                 if mrp_val:
    #                     rec.y_so_origin = mrp_val.y_so_origin

    #                 po_val = self.env['purchase.order'].search([('name','=',rec.origin)])
    #                 if po_val:
    #                     rec.y_so_origin = po_val.y_so_origin

    #                 stock_val = self.env['stock.picking'].search([('name','=',rec.origin)])
    #                 if stock_val:

    #                     rec.y_so_origin = stock_val.origin

    #     else:
    #         raise UserError(_("You are Not Authorised To Update Sale Order"))




class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        for do_pick in self.picking_ids:
            do_pick.write({'y_so_origin': self.name})
        for parent in self.mrp_production_ids:            
            child_lst = []
            new_child_lst = []
            child_lst+= parent._get_children().ids
            for ch in child_lst:
                new_child_lst += self.env['mrp.production'].search([('id','=',ch)])._get_children().ids
                [child_lst.append(x) for x in new_child_lst if x not in child_lst]
            child_lst.append(parent.id)            
            child_lst.sort(reverse=False)
            mo_list = self.env['mrp.production'].search([('id','in',child_lst)])
            mo_list.write({'y_so_origin':self.name,'y_partner_shipping_id':self.partner_shipping_id.id})
            mo_list.picking_ids.write({'y_so_origin':self.name})
        return res


# class MrpProductionNew(models.Model):
#     _inherit = "mrp.production"

#     @api.model
#     def create(self,vals):
#         res = super(MrpProductionNew,self).create(vals)
#         for rec in res:
#             picking_val = self.env['stock.picking'].search([('name','=',rec.origin)])
#             if picking_val:
#                 res.y_so_origin = picking_val.y_so_origin
#                 sale_origin = self.env['sale.order'].search([('name','=',picking_val.y_so_origin)])
#                 rec.partner_shipping_id = sale_origin.partner_shipping_id.id

#         return res

    
class PurchaseorderNew(models.Model):
    _inherit = "purchase.order"


    y_so_origin = fields.Char(string="Saleorder Ref",store=True)


    #this is function is for flow y_so_origin to subcon picking
    def _get_subcontracting_resupplies(self):
        result = super(PurchaseorderNew,self)._get_subcontracting_resupplies()
        for picking in result:
            picking.y_so_origin = self.y_so_origin
        return result

    

    #this is function is for flow y_so_origin from po to normal picking

    def _prepare_picking(self):
        res = super(PurchaseorderNew,self)._prepare_picking()
        for rec in self:
            res['y_so_origin'] = rec.y_so_origin
        return res



    @api.model
    def create(self,vals):
        res = super(PurchaseorderNew,self).create(vals)
        if res.origin:
            mrp_val = self.env['mrp.production'].search([('name','=',res.origin)])
            if mrp_val:
                res.y_so_origin = mrp_val.y_so_origin
        return res

   











   