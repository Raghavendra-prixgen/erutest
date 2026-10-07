from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from odoo import tools


class CogsRegisterReport(models.Model):
    _name = "cogs.register.report"
    _auto = False
    _description = "COGS Register Report"

    y_company_id = fields.Many2one('res.company', string='Company', readonly=True)
    y_journal_id = fields.Many2one('account.journal', 'Journal Name', readonly=True)
    y_account_id = fields.Many2one('account.account', 'Account Name', readonly=True)
    y_move_id = fields.Many2one('account.move', string='Invoice Number')
    y_move_line_id = fields.Many2one('account.move.line')
    y_invoice_date = fields.Date(string='Invoice Date')
    y_currency_id = fields.Many2one('res.currency', string="Currency", readonly=True)

    y_sale_order_id = fields.Many2one('sale.order', string="Sale Order Number")
    y_sale_line_id = fields.Many2one('sale.order.line', string="Sale Order line")
    y_sale_order_date = fields.Datetime(string="Sale Order Date")

    # Partner related fields
    y_partner_id = fields.Many2one('res.partner', string="Partner")
    y_vat = fields.Char(string="Vendor GST No")


    # Product related fields
    y_product_id = fields.Many2one('product.product', string="Product")
    y_label = fields.Char(string="Label")
    y_uom_id = fields.Many2one('uom.uom', string="Product Uom")
    y_hsn_code = fields.Char(string="HSN Code")
    y_product_category_id = fields.Many2one('product.category', string="Product Category")
    y_cogs = fields.Float(string="Cogs Amount")
    y_product_ref = fields.Char(string="Product Code")

    y_quantity = fields.Float('Quantity', readonly=True)
    y_price_unit = fields.Float('Unit Price', readonly=True)
    y_exchange_rate = fields.Float('Exchange Rate', readonly=True)
    y_price_subtotal = fields.Float('Subtotal')

    y_amount_exclusive_tax = fields.Float(string="Amount Exclusive Tax")
    y_amount_inclusive_tax = fields.Float(string="Amount Inclusive Tax")
    y_tax_amount = fields.Float(string="Total Tax Amount", readonly=True)
    y_tax_id_list = fields.Char('List of Tax Id')
    y_discount = fields.Float(string="Discount %")

    y_amount_inr = fields.Float(string="Amount in INR")

   

    # # # COGS Calculation
    # @api.depends('y_move_id', 'y_product_id')
    # def _compute_cogs(self):
    #     for record in self:
    #         record.y_cogs = 0.0
    #         if record.y_product_id and record.y_move_id:
    #             cogs_lines = record.y_move_id.line_ids.filtered(
    #                 lambda l: l.product_id.id == record.y_product_id.id and
    #                         l.cogs_origin_id and
    #                         l.balance > 0
    #             )
    #             record.y_cogs = sum(line.balance for line in cogs_lines)


            

    @api.model
    def cogs_register_query(self, start_date, end_date):
        allowed_company_ids = self.env.context.get('allowed_company_ids', [])

        if not allowed_company_ids:
            allowed_company_ids = [self.env.company.id]

        if isinstance(allowed_company_ids, int):
            allowed_company_ids = (allowed_company_ids,)
        elif isinstance(allowed_company_ids, list):
            if len(allowed_company_ids) == 1:
                allowed_company_ids = (allowed_company_ids[0],)
            else:
                allowed_company_ids = tuple(allowed_company_ids)

        tools.drop_view_if_exists(self._cr, 'cogs_register_report')
        self._cr.execute("""
                CREATE OR REPLACE VIEW cogs_register_report AS (
                    SELECT 
                        row_number() OVER () as id,
                        move.company_id AS y_company_id,
                        move.id AS y_move_id,
                        move.invoice_date AS y_invoice_date,
                        line.name AS y_label,
                        sol.id AS y_sale_line_id,
                        so.id AS y_sale_order_id,
                        so.date_order AS y_sale_order_date,
                        line.product_id AS y_product_id,
                        uom.id AS y_uom_id,
                        pro_categ.id AS y_product_category_id,
                        line.id AS y_move_line_id,
                        line.quantity AS y_quantity,
                        line.price_unit AS y_price_unit,
                        line.price_subtotal AS y_price_subtotal,
                        line.journal_id AS y_journal_id,
                        line.account_id AS y_account_id,
                        array_agg(tax_rel.account_tax_id) AS y_tax_id_list,
                        line.partner_id AS y_partner_id,
                        line.currency_id AS y_currency_id,
                        line.discount AS y_discount,
                        rp.vat as y_vat,
                        pt.l10n_in_hsn_code AS y_hsn_code,
                        product.default_code as y_product_ref,
                        -- COGS Calculation
                        COALESCE((
                            SELECT SUM(cogs_line.balance)
                            FROM account_move_line cogs_line
                            WHERE cogs_line.move_id = move.id
                                AND cogs_line.product_id = line.product_id
                                AND cogs_line.cogs_origin_id = line.id
                                AND cogs_line.balance > 0
                        ), 0.0) as y_cogs,
                        CASE 
                            WHEN line.amount_currency != 0 AND line.balance != 0
                            THEN ABS(line.balance / line.amount_currency)
                            ELSE 1.0 
                        END as y_exchange_rate,
                        
                        line.price_subtotal AS y_amount_exclusive_tax,
                        (line.price_total - line.price_subtotal) AS y_tax_amount,
                       

                        line.price_total AS y_amount_inclusive_tax,
                        (CASE 
                            WHEN line.amount_currency != 0 AND line.balance != 0
                            THEN ABS(line.balance / line.amount_currency)
                            ELSE 1.0 
                        END) * line.price_total AS y_amount_inr
                        
                        
                    FROM account_move move
                    JOIN account_move_line line ON move.id = line.move_id
                    JOIN sale_order_line_invoice_rel sol_rel ON sol_rel.invoice_line_id = line.id
                    JOIN sale_order_line sol ON sol.id = sol_rel.order_line_id
                    JOIN sale_order so ON so.id = sol.order_id
                    LEFT JOIN res_partner rp ON rp.id = move.partner_shipping_id
                    LEFT JOIN product_product product ON product.id = line.product_id
                    LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
                    LEFT JOIN product_category pro_categ ON pro_categ.id = pt.categ_id
                    LEFT JOIN uom_uom uom ON uom.id = pt.uom_id
                    LEFT JOIN account_move_line_account_tax_rel tax_rel ON line.id = tax_rel.account_move_line_id
                    WHERE move.state = 'posted' 
                        AND line.product_id IS NOT NULL 
                        AND (move.move_type = 'out_invoice' OR move.move_type = 'out_refund') 
                        AND move.date BETWEEN %(start_date)s AND %(end_date)s
                        AND move.company_id IN %(companies)s
                    GROUP BY line.name, line.id, sol.id, so.id, pro_categ.id, pt.id, pt.l10n_in_hsn_code, uom.id, 
                            move.id, line.quantity, line.price_unit, line.discount,
                            rp.vat, line.price_subtotal, line.journal_id, line.account_id, line.partner_id, line.currency_id,
                            line.product_id, product.default_code,line.price_total
                )""", {
            'start_date': start_date,
            'end_date': end_date,
            'companies': allowed_company_ids
        })

        return {
            'name': _("COGS Register Report"),
            'type': 'ir.actions.act_window',
            'res_model': 'cogs.register.report',
            'view_mode': 'tree,pivot',
            'views': [(self.env.ref('odoo_e_53.view_cogs_register_report_list').id, 'tree'),
                      (False, 'pivot')],
            'target': 'current',
            'context': dict(self.env.context, allowed_company_ids=allowed_company_ids)
        }
