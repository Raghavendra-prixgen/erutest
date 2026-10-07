# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        if move.y_payment_type == 'outbound':
            res['y_payment_type'] = 'inbound'
        if move.y_payment_type == 'inbound':
            res['y_payment_type'] = 'outbound'
        return res

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_post(self):
        for line in self.line_ids:
            if line.amount < 0:
                line.move_id.y_payment_type = 'outbound'
            else:
                line.move_id.y_payment_type = 'inbound'
        return super(AccountBankStatement, self).button_post()
    

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    y_name_sequence_id = fields.Many2one('ir.sequence')
    y_refund_sequence_id = fields.Many2one('ir.sequence')
    y_out_sequence_id = fields.Many2one('ir.sequence')
    y_in_sequence_id = fields.Many2one('ir.sequence')
    y_recon_sequence_id = fields.Many2one('ir.sequence')

    y_ceiling_limit = fields.Boolean(string="Ceiling Limit")
    y_ceiling_limit_value = fields.Float(string="Ceiling Limit Value")

    y_make_seq_mandetory = fields.Boolean(compute="_get_seq_mand")

    inbound_payment_method_line_ids = fields.One2many(compute=False)
    outbound_payment_method_line_ids = fields.One2many(compute=False)

    @api.depends('type')
    def _get_seq_mand(self):
        for rec in self:
            if rec.type in ('cash','bank'):
                rec.y_make_seq_mandetory = bool(self.env['ir.config_parameter'].sudo().get_param('account_base.y_enable_custom_sequence')) or False
            else:
                rec.y_make_seq_mandetory = False


class AccountMove(models.Model):
    _inherit = 'account.move'

    y_journal_type = fields.Selection(related='journal_id.type', readonly=False, string='JType')
    y_payment_type = fields.Selection(related='payment_id.payment_type', readonly=False)

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        pass

    def _post(self, soft=True):
        for rec in self:
            if rec.move_type == 'entry':
                if rec.journal_id and rec.journal_id.y_ceiling_limit:
                    if sum(rec.line_ids.mapped('credit')) > rec.journal_id.y_ceiling_limit_value:
                        raise UserError(_('Amount should not exceed ceiling amount - %s %s')%(rec.journal_id.y_ceiling_limit_value,rec.currency_id.symbol))
            
            if not rec.posted_before:
                name = 'SEQUENCE NOT MAPPED'
                if rec.move_type in ('in_invoice','in_refund','in_receipt'):
                    if not rec.invoice_date:
                        raise UserError(_('The Bill/Refund date is required to validate this document.'))

                    if rec.date < rec.invoice_date:
                        raise UserError(_('Accounting Date should not less than Bill date !'))
                if rec.y_journal_type in ('cash','bank'):
                    if rec.y_payment_type == 'inbound' and rec.journal_id.y_in_sequence_id:
                        name = rec.journal_id.y_in_sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()
                    elif rec.y_payment_type == 'outbound' and rec.journal_id.y_out_sequence_id:
                        name = rec.journal_id.y_out_sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()
                    elif rec.journal_id.y_recon_sequence_id:
                        name = rec.journal_id.y_recon_sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()
                
                elif rec.move_type in ('in_refund','out_refund') and rec.journal_id.y_refund_sequence_id:
                    name = rec.journal_id.y_refund_sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()
                elif rec.move_type in ('in_invoice','out_invoice') and rec.journal_id.y_name_sequence_id:
                    name = rec.journal_id.y_name_sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()
                elif rec.move_type == 'entry':
                    if rec.journal_id.y_refund_sequence_id:
                        name = rec.journal_id.y_refund_sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()
                    elif rec.journal_id.y_name_sequence_id:
                        name = rec.journal_id.y_name_sequence_id.with_context(ir_sequence_date=rec.date).next_by_id()

                if name == "SEQUENCE NOT MAPPED":
                    raise ValidationError(_(""" Sequence Not Mapped for {} Journal """.format(rec.journal_id.name)))
                rec.name = name
                if rec.payment_id:
                    rec.env.cr.execute("""UPDATE account_move SET name = '{}' WHERE id = {}""".format(name,rec.payment_id.id))
                    
        return super(AccountMove, self)._post(soft)