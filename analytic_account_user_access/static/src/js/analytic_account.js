/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { pick } from "@web/core/utils/objects";
import { Component } from "@odoo/owl";
import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";

console.log("cvdsvcdsvfdvf");


class AnalyticDistribution extends AnalyticDistribution {

    setup(){
        super.setup();
    }
    test(){
        console.log(this.props);
        console.log("bdsadsvcds");
    }

}




// class AnalyticDistributionNew extends AnalyticDistribution {

//    setup(){
//     super.setup();{
//         console.log("vgdsvhfvdsfdvfdvxhfg");
//     }
//     console.log("AnalyticDistributionNew");
//    }
//     recordProps(line) {
//          console.log('222222ssssssssssssssssssss')

//         this.super();

//         console.log("Prakuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu1234")
//         const analyticAccountFields = {
//             id: { type: "int" },
//             display_name: { type: "char" },
//             color: { type: "int" },
//             plan_id: { type: "many2one" },
//             root_plan_id: { type: "many2one" },
//         };
//         let recordFields = {};
//         const values = {};
//         // Analytic Account fields
//         line.analyticAccounts.map((account) => {
//             const fieldName = `x_plan${account.planId}_id`;

//             // const value = pyEnv['res.users'].search([('id','=',2)])
//             // console.log(value,)
//             recordFields[fieldName] = {
//                 string: account.planName,
//                 relation: "account.analytic.account",
//                 type: "many2one",
//                 related: {
//                     fields: analyticAccountFields,
//                     activeFields: analyticAccountFields,
//                 },
//                 // company domain might be required here
//                 domain: [["root_plan_id", "=", account.planId]],
//             };
//             console.log(fieldName,"profileeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")

//             values[fieldName] =  account?.accountId || false;
//         });
//         // Percentage field
//         recordFields['percentage'] = {
//             string: _t("Percentage"),
//             type: "percentage",
//             cellClass: "numeric_column_width",
//             ...this.decimalPrecision,
//         };
//         values['percentage'] = line.percentage;
//         // Value field copied from original
//         if (this.props.amount_field) {
//             const { string, name, type, currency_field } = this.props.record.fields[this.props.amount_field];
//             recordFields[name] = { string, name, type, currency_field, cellClass: "numeric_column_width" };
//             values[name] = this.props.record.data[name] * values['percentage'];
//             // Currency field
//             if (currency_field) {
//                 // TODO: check web_read network request
//                 const { string, name, type, relation } = this.props.record.fields[currency_field];
//                 recordFields[currency_field] = { name, string, type, relation, invisible: true };
//                 values[currency_field] = this.props.record.data[currency_field][0];
//             }
//         }
//         return {
//             fields: recordFields,
//             values: values,
//             activeFields: recordFields,
//             onRecordChanged: async (record, changes) => await this.lineChanged(record, changes, line),
//         }
//     }



// }
// registry.category("fields").add("analytic_distribution_new", AnalyticDistributionNew);


// AnalyticDistributionNew.template = "analytic_account_user_access.AnalyticDistributionNew";
// export const AnalyticDistributionNews = {
//     component: AnalyticDistributionNew,
// };


// return AnalyticDistributionNew;

