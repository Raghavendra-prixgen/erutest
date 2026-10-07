from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplateNew(models.Model):
    _inherit='product.template'

    y_is_editable = fields.Boolean(string="Is editable", compute='get_user_access')

    @api.depends('name')
    def get_user_access(self):
        if self.user_has_groups('cost_edit_access_17.group_for_standard_price_access'):
            self.y_is_editable = True
        else:
            self.y_is_editable = False

