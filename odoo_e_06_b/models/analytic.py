# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    y_business_unit = fields.Boolean()

    @api.onchange('y_business_unit','default_applicability','applicability_ids.applicability')
    def _onchange_business_unit(self):
        if self.y_business_unit and self.default_applicability != 'mandatory':
            self.default_applicability = 'mandatory'

        if self.y_business_unit:
            for line in self.applicability_ids:
                if line.applicability != 'mandatory':
                    line.applicability = 'mandatory'

    def write(self, vals):
        res = super().write(vals)
        self._onchange_business_unit()
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            rec._onchange_business_unit()
        return res

    @api.model
    def get_relevant_plans(self, **kwargs):
        """
        CUSTOMIZATION: Overrides standard applicability logic to support PREFIX-based account code matching (comma-separated, startswith)
        and allows passing a raw 'account_prefix' string instead of only an account.account record. Re-evaluates 'mandatory' vs 'optional'
        after calling super()."""
        # Call standard logic first to get the base list of relevant root plans
        # (already filtered for 'unavailable' plans, includes forced_plans, etc.)
        plans = super().get_relevant_plans(**kwargs)

        # Standard core only accepts an 'account' record for matching.
        # Customization allows passing a raw prefix string directly via 'account_prefix' 
        account = kwargs.get('account')
        if isinstance(account, int):
            account = self.env['account.account'].browse(account)
        account_code = kwargs.get('account_prefix') or (account.code if account else False)

        # Falls back to deriving category from a product if categ not passed directly.
        product_categ = kwargs.get('product_categ')
        if isinstance(product_categ, int):
            product_categ = self.env['product.category'].browse(product_categ)
        if not product_categ:
            product = kwargs.get('product')
            if isinstance(product, int):
                product = self.env['product.product'].browse(product)
            product_categ = product.categ_id if product else False
            
        #accepts either company_id or company kwarg
        company = kwargs.get('company_id') or kwargs.get('company')
        if isinstance(company, int):
            company = self.env['res.company'].browse(company)

        business_domain = kwargs.get('business_domain')

        #enables PREFIX matching (startswith) on comma-separated account codes (e.g. "601,602,700"), unlike standard's exact-match domains.
        def matches_prefix(code, prefix_field):
            if not prefix_field:
                return True
            if not code:
                return False
            return any(code.startswith(p.strip()) for p in prefix_field.split(',') if p.strip())

        #Re-fetch 'mandatory' applicability lines and re-evaluate them using custom prefix logic + optional filters 
        #(business_domain/product_categ/ company)
        applicability_lines = self.env['account.analytic.applicability'].sudo().search([
            ('analytic_plan_id', 'in', [p['id'] for p in plans]),
            ('applicability', '=', 'mandatory'),
        ])

        mandatory_plan_ids = {
            line.analytic_plan_id.id for line in applicability_lines
            if matches_prefix(account_code, line.account_prefix)
            and (not business_domain or line.business_domain == business_domain)
            and (not line.product_categ_id or line.product_categ_id == product_categ)
            and (not line.company_id or line.company_id == company)
        }

        # Overwrite the 'applicability' key computed by the standard method with our own mandatory/optional decision based on prefix matching.
        for plan_vals in plans:
            plan_vals['applicability'] = (
                'mandatory' if plan_vals['id'] in mandatory_plan_ids else 'optional'
            )

        return plans


class AccountAnalyticApplicability(models.Model):
    _inherit = 'account.analytic.applicability'

    business_domain = fields.Selection(
        selection_add=[('stock_move_and_line','Inventory'),
                        ('payment','Payment'),],
        ondelete={'stock_move_and_line': 'cascade','payment': 'cascade',},
    )

    def write(self, vals):
        res = super().write(vals)
        self.analytic_plan_id._onchange_business_unit()
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            rec.analytic_plan_id._onchange_business_unit()
        return res
class AccountAnalyticDistributionModel(models.Model):
    _inherit = 'account.analytic.distribution.model'

    y_warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse' )