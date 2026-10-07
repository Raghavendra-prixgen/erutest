from odoo import models, fields, api, _
import itertools


class MrpReport(models.Model):
    _inherit = 'mrp.report'

    product_category_id = fields.Many2one('product.category',string="Product Category",store=True)


    def _select(self):
        select_str = """
            SELECT
                min(mo.id)             AS id,
                mo.id                  AS production_id,
                mo.company_id          AS company_id,
                rc.currency_id         AS currency_id,
                mo.date_finished       AS date_finished,
                mo.product_id          AS product_id,
                mo.product_category_id AS product_category_id,
                prod_qty.product_qty   AS qty_produced,
                comp_cost.total * currency_table.rate                                                                                   AS component_cost,
                op_cost.total * currency_table.rate                                                                                     AS operation_cost,
                (comp_cost.total + op_cost.total) * currency_table.rate                                                                 AS total_cost,
                op_cost.total_duration                                                                                                  AS duration,
                comp_cost.total * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate                    AS unit_component_cost,
                op_cost.total * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate                      AS unit_operation_cost,
                (comp_cost.total + op_cost.total) * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate  AS unit_cost,
                op_cost.total_duration / prod_qty.product_qty                                                                           AS unit_duration,
                (comp_cost.total + op_cost.total) * cost_share.byproduct_cost_share * currency_table.rate                               AS byproduct_cost,
                sub_cost.total * currency_table.rate                                                                    AS subcontracting_cost,
                sub_cost.total * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate     AS unit_subcontracting_cost

        """

        return select_str


class Operation(models.Model):
    _inherit = 'mrp.routing.workcenter'

    is_master = fields.Boolean()

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_category_id = fields.Many2one('product.category',string="Product Category",related='product_id.categ_id',store=True)
    item_group = fields.Many2one('item.group',related="product_id.product_tmpl_id.item_group",store=True)
    product_group_1 = fields.Many2one('product.group.1',related="product_id.product_tmpl_id.product_group_1",store=True)
    product_group_2 = fields.Many2one('product.group.2',related="product_id.product_tmpl_id.product_group_2",store=True)
    product_group_3 = fields.Many2one('product.group.3',related="product_id.product_tmpl_id.product_group_3",store=True)

