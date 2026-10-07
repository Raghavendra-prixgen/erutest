from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CogsRegisterReportWizard(models.TransientModel):
    _name = "cogs.register.wizard"
    _description = "COGS Register Report Wizard"

    y_start_date = fields.Date('Start Date', required=True)
    y_end_date = fields.Date('End Date', required=True)
    y_company_ids = fields.Many2many('res.company', string='Company')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'y_company_ids' in fields_list:
            res['y_company_ids'] = [(6, 0, [self.env.company.id])]
        return res

    def retrieve_register(self):
        company_ids = self.y_company_ids.ids if self.y_company_ids else [self.env.company.id]
        context = dict(self.env.context)
        context['allowed_company_ids'] = company_ids

        return self.env['cogs.register.report'].with_context(context).cogs_register_query(
            self.y_start_date,
            self.y_end_date
        )

    
    @api.constrains('y_start_date', 'y_end_date')
    def _check_date_range(self):
        for record in self:
            if record.y_start_date and record.y_end_date and record.y_start_date > record.y_end_date:
                raise ValidationError(_('End Date must be greater than Start Date.'))