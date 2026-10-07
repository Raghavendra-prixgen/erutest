from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.constrains('product_id', 'picking_id')
    def _check_product_category_match(self):
        for move in self:
            picking_type = move.picking_id.picking_type_id
            product = move.product_id

            if not (picking_type and product):
                continue

            if picking_type.y_consumable and picking_type.y_product_category:
                allowed_categories = picking_type.y_product_category.ids
                if product.categ_id.id not in allowed_categories:
                    allowed_category_names = ', '.join(picking_type.y_product_category.mapped('name'))
                    raise ValidationError(
                        f"The selected product '{product.display_name}' does not belong to the allowed categories for this operation type." "\n"
                        f"Please select a product from one of the following categories: {allowed_category_names}"
                    )
