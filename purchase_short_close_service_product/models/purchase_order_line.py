
from odoo import models, fields, api, _
from odoo.exceptions import UserError



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


   # ==============================================================
    # PENDING QTY — override to force 0 when short closed
    # ==============================================================
    @api.depends(
        "product_qty",
        "qty_received",
        "y_is_short_close",
    )
    def get_y_pending_qty(self):
        # Run the base (already-working) computation first
        super().get_y_pending_qty()

        # Then override: short closed lines have nothing pending,
        # regardless of product type (service or storable).
        for line in self:
            if line.y_is_short_close:
                line.y_pending_qty = 0.0

    # ==============================================================
    # INVOICE STATUS — override to force 'full' when short closed
    # ==============================================================
    @api.depends(
        "state",
        "qty_received",
        "qty_invoiced",
        "product_qty",
        "y_is_short_close",
    )
    def _compute_y_invoice_status(self):
        # Run the base (already-working) computation first
        super()._compute_y_invoice_status()

        # Then override: short closed lines are considered fully
        # billed — this applies to service products too, since a
        # service line has no receipt/qty_received concept and its
        # base logic already keys off product_qty vs qty_invoiced.
        for line in self:
            if line.y_is_short_close:
                line.y_invoice_status = "full"
                line.order_id.invoice_status = "invoiced" 
                line.order_id.y_is_po_short_close = True                                                                      


    @api.depends(
        "product_qty",
        "qty_received",
        "qty_invoiced",
        "y_is_short_close",
        "product_id",
        "order_id.state",
    )
    def _compute_qty_to_invoice(self):
        super()._compute_qty_to_invoice()

        for line in self:
            if line.y_is_short_close:
                line.qty_to_invoice = 0

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self):
        for order in self:
            short_closed_lines = order.order_line.filtered(
                lambda line: line.y_is_short_close
            )

            # Temporarily prevent short-closed lines from being invoiced
            for line in short_closed_lines:
                line.qty_to_invoice = 0

        return super().action_create_invoice()
    


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        res = super()._onchange_purchase_auto_complete()

        for move in self:
            short_closed_lines = move.invoice_line_ids.filtered(
                lambda line: (
                    line.purchase_line_id
                    and line.purchase_line_id.y_is_short_close
                )
            )

            if short_closed_lines:
                move.invoice_line_ids -= short_closed_lines

        return res