# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from num2words import num2words
from odoo.tools import float_compare, float_round, float_is_zero, OrderedSet
import json


class AccountMoveCustomReport(models.Model):
    _inherit = "account.move"

    def fetch_sale_order(self):
        sale_order_ids = self.invoice_line_ids[0].sale_line_ids.order_id.id
        sale_id = self.env["sale.order"].browse(sale_order_ids)
        return sale_id

    def get_taxes_group_values(self):
        tax_name = []
        taxess = []
        taxes = []
        sorted_tax = []
        for line in self.invoice_line_ids:
            curr_val = line.price_subtotal
            tot_rax_rate = 0.0
            igst_val = 0.0

            sgst_rate = 0.0
            sgst_val = 0.0

            cgst_rate = 0.0
            cgst_val = 0.0

            tcs_rate = 0.0
            tcs_val = 0.0
            cess_val = 0.0
            group = ""

            for each_tax in line.tax_ids:
                if each_tax:
                    tax_name.append(each_tax)
                    if each_tax.amount_type == "group":
                        if each_tax.tax_group_id.name == "GST":
                            for each_group_line in each_tax.children_tax_ids:
                                group = each_tax.tax_group_id.name
                                if (
                                    each_group_line.tax_group_id.name == "SGST"
                                    or each_group_line.tax_group_id.name == "CGST"
                                ):
                                    tot_rax_rate += round(each_group_line.amount, 2)
                                    sgst_val = round(
                                        curr_val * (each_group_line.amount / 100), 2
                                    )
                                elif each_group_line.tax_group_id.name == "TCS":
                                    tcs_rate = each_group_line.amount
                                    tcs_val = round(
                                        (curr_val + sgst_val * 2)
                                        * (each_group_line.amount / 100),
                                        2,
                                    )

                        elif each_tax.tax_group_id.name == "IGST":
                            for each_group_line in each_tax.children_tax_ids:
                                group = each_tax.tax_group_id.name
                                if each_group_line.tax_group_id.name != "TCS":
                                    tot_rax_rate += round(each_tax.amount, 2)
                                    igst_val = round(
                                        curr_val * (each_tax.amount / 100), 2
                                    )
                                elif each_group_line.tax_group_id.name == "TCS":
                                    tcs_rate = each_group_line.amount
                                    tcs_val = round(
                                        (curr_val + igst_val)
                                        * (each_group_line.amount / 100),
                                        2,
                                    )

                    else:
                        val = self.tax_totals
                        val_dict = val
                        for value in val_dict.get("groups_by_subtotal").get(
                            "Untaxed Amount"
                        ):
                            if value.get("tax_group_name") == "Cess":
                                cess_val = value.get("tax_group_amount")
                        group = each_tax.tax_group_id.name
                        tot_rax_rate += round(each_tax.amount)
                        igst_val = round(curr_val * (each_tax.amount / 100), 2)
                    # taxes.append({'hsn':line.product_id.l10n_in_hsn_code,'tax':line.tax_ids,'tax_rate':tot_rax_rate,'igst':igst_val,'sgst':sgst_val,'tcs':tcs_val,'tcs_rate':tcs_rate, 'tax_group':group,'cess_val':cess_val})
                    taxess.append(
                        {
                            "tax": line.tax_ids,
                            "tax_rate": tot_rax_rate,
                            "tcs": tcs_val,
                            "tcs_rate": tcs_rate,
                            "tax_group": group,
                            "cess_val": cess_val,
                        }
                    )

                    for each_tax_id in tax_name:
                        tot_rax_rate = 0.0
                        igst_val = 0.0
                        sgst_val = 0.0
                        tcs_val = 0.0
                        tcs_rate = 0.0
                        group = ""

                        for each_rec in taxes:
                            print("iuytfjkuytf", each_rec["tax"])
                            print("wertyuilm", each_tax_id)

                            if each_tax_id.id == each_rec["tax"]:
                                tot_rax_rate = each_rec["tax_rate"]
                                tcs_rate = each_rec["tcs_rate"]
                                igst_val += each_rec["igst"]
                                sgst_val += each_rec["sgst"]
                                tcs_val += each_rec["tcs"]
                                group = each_rec["tax_group"]
                            else:
                                # tot_rax_rate = each_rec['tax_rate']
                                # igst_val = each_rec['igst']line.tax_id
                                # sgst_val = each_rec['sgst']
                                # tcs_val = each_rec['tcs']
                                # group = each_rec['tax_group']
                                continue

                        sorted_tax.append(
                            {
                                "tax": each_tax_id,
                                "tax_rate": tot_rax_rate,
                                "igst": igst_val,
                                "sgst": sgst_val,
                                "tcs": tcs_val,
                                "tcs_rate": tcs_rate,
                                "tax_group": group,
                            }
                        )
        print(sorted_tax, 1111111111111111111111111111111111111111111111111, taxess)

        result = [
            dict(tupleized) for tupleized in set(tuple(item.items()) for item in taxess)
        ]

        result.reverse()

        tax_name = list(set(tax_name))
        return result
