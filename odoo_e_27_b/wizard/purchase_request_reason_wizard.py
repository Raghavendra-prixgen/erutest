# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseRequestReasonWizard(models.TransientModel):
    _name = "purchase.request.reason.wizard"
    _description = "Purchase Request Cancel/Reject Reason"

    y_request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        required=True,
        readonly=True,
    )
    y_action_type = fields.Selection(
        selection=[("cancel", "Cancel"), ("reject", "Reject")],
        string="Action",
        required=True,
        readonly=True,
    )
    y_reason = fields.Text(
        string="Reason",
        required=True,
    )

    def button_confirm(self):
        self.ensure_one()
        if not self.y_reason or not self.y_reason.strip():
            raise ValidationError(_("Please enter a reason before confirming."))

        if self.y_action_type == "cancel":
            self.y_request_id.write({
                "state": "cancel",
                "y_cancel_reason": self.y_reason,
            })
        else:
            self.y_request_id.mapped("line_ids").do_cancel()
            self.y_request_id.write({
                "state": "rejected",
                "y_reject_reason": self.y_reason,
            })
        return {"type": "ir.actions.act_window_close"}