# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "analytic.mixin"]
    _order = "id desc"

    name = fields.Char(string="Description", tracking=True)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        tracking=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    product_qty = fields.Float(
        string="Quantity", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        related="request_id.description",
        string="PR Description",
        store=True,
        readonly=False,
    )
    origin = fields.Char(
        related="request_id.origin", string="Source Document", store=True
    )
    date_required = fields.Date(
        string="Required Date",
        required=True,
        tracking=True,
        default=fields.Date.context_today,
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    specifications = fields.Text()
    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        store=True,
    )
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Preferred supplier",
        compute="_compute_supplier_id",
        compute_sudo=True,
        store=True,
    )
    cancelled = fields.Boolean(readonly=True, default=False, copy=False)

    purchased_qty = fields.Float(
        string="RFQ/PO Qty",
        digits="Product Unit of Measure",
        compute="_compute_purchased_qty",
    )
    purchase_lines = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_request_line_id",
        column2="purchase_order_line_id",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self: self.env["purchase.order"]._fields["state"].selection,
        store=True,
    )
    move_dest_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="created_purchase_request_line_id",
        string="Downstream Moves",
    )

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Orderpoint"
    )
    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_request_line_id",
        string="Purchase Request Allocation",
    )

    qty_in_progress = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty_cancelled",
        store=True,
        help="Quantity cancelled",
    )
    qty_to_buy = fields.Boolean(
        compute="_compute_qty_to_buy",
        string="There is some pending qty to buy",
        store=True,
    )
    pending_qty_to_receive = fields.Float(
        compute="_compute_qty_to_buy",
        digits="Product Unit of Measure",
        copy=False,
        string="Pending Qty to Receive",
        store=True,
    )
    estimated_cost = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        help="Estimated cost of Purchase Request Line, not propagated to PO.",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        tracking=True,
    )
    line_status = fields.Selection([('draft','Draft'),('partial','Partial'),('done','Done')],compute='_compute_line_status')


    def _validate_analytic_distribution(self):
        for line in self:
            #enforce analytic validation
            line.with_context(validate_analytic = True)._validate_distribution(**{
                'product': line.product_id.id,
                'business_domain': 'purchase_request',
                'company_id': line.company_id.id,
            })

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "request_id.state",
        "product_qty",
    )
    def _compute_qty_to_buy(self):
        for pr in self:
            qty_to_buy = sum(pr.mapped("product_qty")) - sum(pr.mapped("qty_done"))
            pr.qty_to_buy = qty_to_buy > 0.0
            pr.pending_qty_to_receive = qty_to_buy

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty(self):
        for request in self:
            done_qty = sum(
                request.purchase_request_allocation_ids.mapped("allocated_product_qty")
            )
            open_qty = sum(
                request.purchase_request_allocation_ids.mapped("open_product_qty")
            )
            request.qty_done = done_qty
            request.qty_in_progress = open_qty

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.order_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty_cancelled(self):
        for request in self:
            if request.product_id.type != "service":
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.stock_move_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
            else:
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.purchase_line_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
                # done this way as i cannot track what was received before
                # cancelled the purchase order
                qty_cancelled -= request.qty_done
            if request.product_uom_id:
                request.qty_cancelled = (
                    max(
                        0,
                        request.product_id.uom_id._compute_quantity(
                            qty_cancelled, request.product_uom_id
                        ),
                    )
                    if request.purchase_request_allocation_ids
                    else 0
                )
            else:
                request.qty_cancelled = qty_cancelled

    @api.depends(
        "purchase_lines",
        "request_id.state",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False

    @api.depends("product_id", "product_id.seller_ids")
    def _compute_supplier_id(self):
        for rec in self:
            sellers = rec.product_id.seller_ids.filtered(
                lambda si, rec=rec: not si.company_id or si.company_id == rec.company_id
            )
            rec.supplier_id = sellers[0].partner_id if sellers else False

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(self.product_id.code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
            # self.estimated_cost = self.env['purchase.order.line'].search([('product_id','=',self.product_id.id)],order='date_approve asc', limit=1).price_unit
            self.estimated_cost = self.product_id.standard_price
    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def write(self, vals):
        res = super(PurchaseRequestLine, self).write(vals)
        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res

    # def _compute_purchased_qty(self):
    #     for rec in self:
    #         rec.purchased_qty = sum(rec.purchase_lines.filtered(lambda x:x.state in ('done','purchase')).mapped('product_qty'))


    def _compute_purchased_qty(self):
        for rec in self:
            total_request_qty = 0.0  # Initialize total requested quantity
            for alloc in rec.purchase_request_allocation_ids:
                if alloc.purchase_line_id.state not in ('cancel','reject'):
                
                    total_request_qty += alloc.requested_product_uom_qty  # Total requested qty
                # print("Total Request Qty:", total_request_qty)
                    # if total_request_qty > 0:
                    #     # Distribute purchased quantity based on request qty proportion
                    #     proportion = rec.product_qty / total_request_qty
                    #     total_purchased_qty += po_line.product_qty * proportion
            rec.purchased_qty = total_request_qty
            # print("Total Purchased Qty:", rec.purchased_qty)
    

    # def _compute_purchased_qty(self):
    #     for rec in self:
    #         rec.purchased_qty = 0.0
    #         for line in rec.purchase_lines.filtered(lambda x: x.state != "cancel"):
    #             if rec.product_uom_id and line.product_uom != rec.product_uom_id:
    #                 rec.purchased_qty += line.product_uom._compute_quantity(
    #                     line.product_qty, rec.product_uom_id
    #                 )
    #             else:
    #                 rec.purchased_qty += line.product_qty

    @api.depends("purchase_lines.state", "purchase_lines.order_id.state")
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any(po_line.state == "done" for po_line in rec.purchase_lines):
                    temp_purchase_state = "done"
                elif all(po_line.state == "cancel" for po_line in rec.purchase_lines):
                    temp_purchase_state = "cancel"
                elif any(po_line.state == "purchase" for po_line in rec.purchase_lines):
                    temp_purchase_state = "purchase"
                elif any(
                    po_line.state == "to approve" for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "to approve"
                elif any(po_line.state == "sent" for po_line in rec.purchase_lines):
                    temp_purchase_state = "sent"
                elif all(
                    po_line.state in ("draft", "cancel")
                    for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "draft"
            rec.purchase_state = temp_purchase_state
            rec.request_id.compute_is_all_lines_done()

            # request_id_state =  [True if line.purchase_state in ['purchase','done'] else False for line in rec.request_id.line_ids]
            # is_all_qty_done = False
            # for line in rec.request_id.line_ids:
            #     purchase_done_quantity = sum(line.purchase_lines.filtered(lambda x:x.state in ('done','purchase')).mapped('product_qty'))
            #     if line.product_qty <= purchase_done_quantity:
            #         is_all_qty_done = True
            #
            # if any(rec.request_id.line_ids.filtered(lambda x:x.purchased_qty > 0 and (rec.purchased_qty != rec.product_qty or rec.purchased_qty == rec.product_qty))):
            #     rec.request_id.write({"state": "partial"})
            #
            # is_done_list = [True if line.purchased_qty == line.product_qty else False for line in rec.request_id.line_ids]
            # if all(is_done_list):
            #     rec.request_id.write({"state": "done"})

    @api.depends('purchase_request_allocation_ids.purchase_line_id.state')
    def _compute_line_status(self):
        for data in self:
            total_qty = sum(data.purchase_request_allocation_ids.mapped("allocated_product_qty"))
            print(data.product_qty,'total qty')
            if data.product_qty <= data.purchased_qty:
                all_done_or_purchase = all(
                    line.purchase_line_id.state in ['done', 'purchase']
                    for line in data.purchase_request_allocation_ids if line.purchase_line_id
                )
                print(all_done_or_purchase,'all_done_or_purchase')
                if all_done_or_purchase:
                    data.line_status = 'done'
                else:
                    data.line_status = 'partial'
            if data.product_qty > data.purchased_qty:
                data.line_status = 'partial'
            if data.purchased_qty == 0:
                data.line_status = 'draft'

            # Check if all purchase lines are in 'done' or 'purchase' state


            total_allocated_qty = total_qty  # Store total allocated quantity
            # data.all_lines_done_or_purchase = all_done_or_purchase  # Boolean field to store the check result



    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        if self.mapped("purchase_lines"):
            raise UserError(
                _("You cannot delete a record that refers to purchase lines!")
            )
        for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a purchase request line "
                        "if the purchase request is in draft state."
                    )
                )
        return super(PurchaseRequestLine, self).unlink()

    @api.model
    def _get_supplier_min_qty(self, product, partner_id=False):
        seller_min_qty = 0.0
        if partner_id:
            seller = product.seller_ids.filtered(
                lambda r: r.partner_id == partner_id
            ).sorted(key=lambda r: r.min_qty)
        else:
            seller = product.seller_ids.sorted(key=lambda r: r.min_qty)
        if seller:
            seller_min_qty = seller[0].min_qty
        return seller_min_qty

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id
        # TODO: Not implemented yet.
        #  Make sure we use the minimum quantity of the partner corresponding
        #  to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if not po_line.order_id.dest_address_id:
            supplierinfo_min_qty = self._get_supplier_min_qty(
                po_line.product_id, po_line.order_id.partner_id
            )

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        if new_pr_line:
            print('test123')
            rl_qty = po_line.product_uom_qty
        else:
            for prl in po_line.purchase_request_lines:
                for alloc in prl.purchase_request_allocation_ids:
                    rl_qty += alloc.product_uom_id._compute_quantity(
                        alloc.requested_product_uom_qty, purchase_uom
                    )
        qty = max(rl_qty, supplierinfo_min_qty)
        print(rl_qty,'rl_qty------------',supplierinfo_min_qty,'----------supplierinfo_min_qty')
        return qty
    

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref("odoo_e_27_b.view_purchase_request_line_details")
        return {
            "name": _("Detailed Line"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "purchase.request.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(
                self.env.context,
            ),
        }
