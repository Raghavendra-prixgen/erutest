from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ReportAccountAgedPayableMsme(models.Model):
    _name = "account.aged.payable.msme"
    _description = "Msme Payable "
    # _inherit = "account.aged.partner"
    inherit = "account.report"
    # _auto = False

    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportAccountAgedPayableMsme, self)._get_options(previous_options=previous_options)
        options['filter_partner_type'] = 'msme'
        options['filter_account_type'] = 'payable'

        return options

    @api.model
    def _get_report_name(self):
        return _("Msme Payable")

    @api.model
    def _get_templates(self):
        # OVERRIDE
        templates = super(ReportAccountAgedPayableMsme, self)._get_templates()
        templates['line_template'] = 'account_reports.line_template_aged_payable_report'
        return templates




class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.model
    def _get_options_all_entries_domain(self, options):
        if options.get('filter_partner_type') == 'msme':
            print()
            if not options.get('all_entries'):
                return [('move_id.state', '=', 'posted'),('move_id.partner_id.y_msme_registered', '=', True)]
            else:
                return [('move_id.state', '!=', 'cancel')]

        else:
            if not options.get('all_entries'):
                return [('move_id.state', '=', 'posted')]
            else:
                return [('move_id.state', '!=', 'cancel')]
