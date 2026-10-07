from odoo import models, fields, api, _

class SaleRegisterReportWizard(models.TransientModel):
    _name = "sale.register.wizard"
    _description = " "

    y_name  = fields.Char()
    y_start_date = fields.Date('Start Date')
    y_end_date = fields.Date('End Date')
    # category_id =fields.Many2one('product.category', string='Product Category')

    # Calling report method
    def retrieve_register(self):
        
        return self.env['sales.register.report'].sale_register_query(self.y_start_date, self.y_end_date)

    # Validation for start date and end date
    @api.onchange('y_start_date','y_end_date')
    def date_validation(self):
        if self.y_start_date and self.y_end_date:
            if not self.y_start_date <= self.y_end_date:
                self.y_end_date = False
                return {'warning': {
            'title': _('User Warning'),
            'message': _('Selected End Date must be greater than Selected Start Date!')
        }}
