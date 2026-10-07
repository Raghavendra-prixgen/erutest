from odoo import models, fields, api, _
from datetime import date,datetime
import time
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductTemplateProductGroup(models.Model):
    _inherit = "product.template"

    def write(self,vals):
        if vals.get('y_product_group_2') == False and self.y_product_group_1:
            raise UserError(_('product Group2 is not Mapped'))
    
        if vals.get('y_product_group_3') == False and self.y_product_group_2:
            raise UserError(_('product Group3 is not Mapped'))
        return super().write(vals)