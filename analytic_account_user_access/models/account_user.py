from odoo import fields, models


class AnalyticAccountUserAccessCustom(models.Model):
    _inherit = 'res.users'

    y_analytic_ids = fields.Many2many(
        'account.analytic.account',
        string="Analytic Account",
    )

    def _refresh_analytic_rule(self):
        """Force Odoo to re-evaluate the analytic account record rule
        by toggling it inactive/active, so mapping changes take
        effect immediately without a server restart."""
        record_rule_ids = self.env['ir.rule'].search([
            ('model_id.model', '=', 'account.analytic.account'),
            ('active', '=', True),
        ])
        record_rule_ids.write({'active': False})
        record_rule_ids.write({'active': True})

    def write(self, vals):
        res = super().write(vals)
        if 'y_analytic_ids' in vals:
            self._refresh_analytic_rule()
        return res