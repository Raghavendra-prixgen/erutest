from odoo import models, fields, api, _
from num2words import num2words


def get_selection_label(self, object, field_name, field_value):
    return (dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
    

    
class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    product_code = fields.Char(tracking=True)
    
    delay = fields.Integer(tracking=True)
    
    date_start = fields.Date(tracking=True)
    date_end = fields.Date(tracking=True)
    company_id = fields.Many2one(tracking=True)
    
    
class SaleDocumentType(models.Model):
    _inherit = 'sale.doc.type'
    
    y_name = fields.Char(tracking=True)
    y_description = fields.Char(tracking=True)
    y_sequence_id = fields.Many2one(tracking=True)
    y_company_id = fields.Many2one(tracking=True)



class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    replenish_location = fields.Boolean(tracking=True)
    is_subcontracting_location = fields.Boolean(tracking=True)
    return_location = fields.Boolean(tracking=True)
    scrap_location =  fields.Boolean(tracking=True)
    y_destructive_location = fields.Boolean(tracking=True)
    y_reject_location = fields.Boolean(tracking=True)
    storage_category_id = fields.Many2one(tracking=True)
    y_location_category = fields.Selection(tracking=True)
    cyclic_inventory_frequency = fields.Integer(tracking=True)
     
class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    y_internal_reference_sequence_id = fields.Many2one(tracking=True)
    route_ids = fields.Many2many(tracking=True)
    packaging_reserve_method = fields.Selection(tracking=True)
    property_stock_account_production_cost_id = fields.Many2one(tracking=True)
    y_description = fields.Char(tracking=True)
    
    
    
class UnitOfMeasureCategory(models.Model):
    _name = 'uom.category'
    _inherit = ['uom.category', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    
    def write(self,vals):
        new_dist = []
        if vals.get('uom_ids'):
            new_list = []
            for list1 in vals.get('uom_ids'):
                if list1[-1] != False:
                    new_list.append(list1)
                    uom_ids = self.uom_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
                    new_dist = []
                    for dicts in uom_ids:
                        for newval in new_list:
                            if not isinstance(newval[-1],int):
                                if newval[1] == dicts.id:
                                    if newval[-1].get('y_weight_uom') and dicts.y_weight_uom:
                                        new_y_weight_uom = get_selection_label(self,'uom.uom','y_weight_uom',newval[-1].get('y_weight_uom'))
                                        old_y_weight_uom = get_selection_label(self,'uom.uom','y_weight_uom',dicts.y_weight_uom)
                                        new_dist.append('{} for {}:{} ---> {}'.format("Weight Unit of Measure",dicts.name,old_y_weight_uom,new_y_weight_uom))

                                    if newval[-1].get('name'):
                                        new_name = newval[-1].get('name')
                                        new_dist.append('{}{} ---> {}'.format("Unit of Measure : ",dicts.name,new_name))
                                        
                                    if newval[-1].get('l10n_in_code'):
                                        new_name = newval[-1].get('l10n_in_code')
                                        new_dist.append('{}{} ---> {}'.format("Indian GST UQC : ",dicts.l10n_in_code,new_name))


                                    if newval[-1].get('uom_type') and dicts.uom_type:
                                        new_uom_type = get_selection_label(self,'uom.uom','uom_type',newval[-1].get('uom_type'))
                                        old_uom_type = get_selection_label(self,'uom.uom','uom_type',dicts.uom_type)
                                        new_dist.append('{} for :{} ---> {}'.format("Type",old_uom_type,new_uom_type))

                                    if newval[-1].get('ratio'):
                                        new_ratio = newval[-1].get('ratio')
                                        new_dist.append('{} for {}:{} ---> {}'.format("Ratio: ",dicts.name,dicts.ratio,new_ratio))

                                    if newval[-1].get('rounding'):
                                        new_rounding = newval[-1].get('rounding')
                                        new_dist.append('{} for {}:{} ---> {}'.format("Rounding",dicts.name,dicts.rounding,new_rounding))
                                
            if new_dist:
                msg = ', '.join(dic for dic in new_dist)
                if self.env.user:
                    self.message_post(body=msg)                
        
        return super().write(vals)

    
    
    # def write(self,vals):
    #     if vals.get('uom_ids'):
    #         # if vals.get('uom_ids'):                
    #         new_list = []
    #         for list1 in vals.get('uom_ids'):
    #             if list1[-1] != False:
    #                 new_list.append(list1)
    #                 currency_lines_ids = self.uom_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
    #                 new_dist = []
    #                 for dicts in currency_lines_ids:
    #                     for newval in new_list:
    #                         if newval[1] == dicts.id:                     
                               
    #                             if newval[-1].get('name'):                         
    #                                 new_dist.append('({}--->{}--->{})'.format("Unit of Measure:",dicts.name,newval[-1].get('name')))
                                    
    #                             if newval[-1].get('l10n_in_code'):                         
    #                                 new_dist.append('({}--->{}--->{})'.format("Indian GST UQC:",dicts.l10n_in_code,newval[-1].get('l10n_in_code')))
                                    
    #                             if newval[-1].get('uom_type'):                         
    #                                 new_dist.append('({}--->{}--->{})'.format("Type:",dicts.uom_type,newval[-1].get('uom_type')))
                                    
    #                             if newval[-1].get('ratio'):                         
    #                                 new_dist.append('({}--->{}--->{})'.format("Ratio:",dicts.ratio,newval[-1].get('ratio')))
                                    
    #                             if newval[-1].get('active'):                         
    #                                 new_dist.append('({}--->{}--->{})'.format("Active:",dicts.active,newval[-1].get('active')))
                                    
    #                             if newval[-1].get('rounding'):                         
    #                                 new_dist.append('({}--->{}--->{})'.format("Rounding:",dicts.rounding,newval[-1].get('rounding')))
                                    
    #         if new_dist:
    #                 msg = ', '.join(dic for dic in new_dist)
    #                 self.message_post(body=msg)
    #     res = super(UnitOfMeasureCategory,self).write(vals)
    #     return res
    
    
    
class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    name = fields.Char(tracking=True)
    company_id = fields.Many2one(tracking=True)
    user_id = fields.Many2one(tracking=True)
    use_leads = fields.Boolean(tracking=True)
    use_opportunities = fields.Boolean(tracking=True)
    # alias_contact = fields.Selection(tracking=True)
    alias_name = fields.Char(tracking=True)
    invoiced_target = fields.Float(tracking=True)
    
class ShippingMethod(models.Model):
    _name = 'shipping.method'
    _inherit = ['shipping.method', 'mail.thread', 'mail.activity.mixin']


    y_shipping_method = fields.Char(tracking=True)
    
class UomLogs(models.Model):
    _name = 'uom.uom'
    _inherit = ['uom.uom', 'mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True)
    category_id = fields.Many2one(tracking=True)
    uom_type = fields.Selection(tracking=True)
    factor = fields.Float(tracking=True)
    active = fields.Boolean(tracking=True)
    rounding = fields.Float(tracking=True)
    
class SaleDocumentNotification(models.Model):
    _name = 'sale.document.notification'
    _inherit = ['sale.document.notification', 'mail.thread', 'mail.activity.mixin']

class SaleDocumentNotification(models.Model):
    _name = 'sale.document.notification'
    _inherit = ['sale.document.notification', 'mail.thread', 'mail.activity.mixin']
    
    
class StockWarehouse(models.Model):
    _name = 'stock.warehouse'
    _inherit = ['stock.warehouse', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)
    y_pacakging_sequence = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    partner_id = fields.Many2one(tracking=True)
    reception_steps = fields.Selection(tracking=True)
    delivery_steps = fields.Selection(tracking=True)
    
    buy_to_resupply = fields.Boolean(tracking=True)
    subcontracting_dropshipping_to_resupply = fields.Boolean(tracking=True)
    subcontracting_to_resupply = fields.Boolean(tracking=True)
    manufacture_to_resupply = fields.Boolean(tracking=True)
    manufacture_steps = fields.Selection(tracking=True)
    
class StockRoute(models.Model):
    _name = 'stock.route'
    _inherit = ['stock.route', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    sequence = fields.Integer(tracking=True)
    supplied_wh_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    
    # rule_ids = fields.One2many('stock.rule', 'route_id', 'Rules', copy=True)
    product_categ_selectable = fields.Boolean(tracking=True)
    product_selectable = fields.Boolean(tracking=True)
    packaging_selectable = fields.Boolean(tracking=True)
    shipping_selectable = fields.Boolean(tracking=True)
    y_po_lines = fields.Boolean(tracking=True)
    
    warehouse_selectable = fields.Boolean(tracking=True)
    sale_selectable = fields.Boolean(tracking=True)
    
class ProductPackaging(models.Model):
    _name = 'product.packaging'
    _inherit = ['product.packaging', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    product_id = fields.Many2one(tracking=True)

    sales = fields.Boolean(tracking=True)
    purchase = fields.Boolean(tracking=True)
    package_type_id = fields.Many2one(tracking=True)
    qty = fields.Float(tracking=True)
    barcode = fields.Char(tracking=True)
    company_id = fields.Many2one(tracking=True)

class AccountPaymentTerm(models.Model):
    _name = 'account.payment.term'
    _inherit = ['account.payment.term', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    # line_ids = fields.One2many('account.payment.term.line', 'payment_id', string='Terms', copy=True, default=_default_line_ids)
    company_id = fields.Many2one(tracking=True)
    
    early_discount = fields.Boolean(tracking=True)
    
    discount_percentage = fields.Float(tracking=True)
    
    discount_days = fields.Integer(tracking=True)
    
    
    def write(self,vals):
        new_dist = []
        if vals.get('line_ids'):
            new_list = []
            for list1 in vals.get('line_ids'):
                if list1[-1] != False:
                    new_list.append(list1)
                    line_ids = self.line_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
                    new_dist = []
                    for dicts in line_ids:
                        for newval in new_list:
                            if not isinstance(newval[-1],int):
                                if newval[1] == dicts.id:
                                    if newval[-1].get('value_amount'):
                                        new_name = newval[-1].get('value_amount')
                                        new_dist.append('{}{} ---> {}'.format("Due : ",dicts.value_amount,new_name))
                                        
                                    # if newval[-1].get('value'):
                                    #     new_name = newval[-1].get('value')
                                    #     new_dist.append('{}{} ---> {}'.format(" : ",dicts.value,new_name))
                                        
                                    if newval[-1].get('y_advance_request_required'):
                                        new_name = newval[-1].get('y_advance_request_required')
                                        new_dist.append('{}{} ---> {}'.format("Down Payment Request : ",dicts.y_advance_request_required,new_name))


                                    if newval[-1].get('nb_days'):
                                        new_name = newval[-1].get('nb_days')
                                        new_dist.append('{}{} ---> {}'.format("After : ",dicts.nb_days,new_name))
                                        
                                    
                                    # if newval[-1].get('delay_type'):
                                    #     new_rounding = newval[-1].get('delay_type')
                                    #     new_dist.append('{} for {}:{} ---> {}'.format("Rounding",dicts.delay_type,new_rounding))
                                
            if new_dist:
                msg = ', '.join(dic for dic in new_dist)
                if self.env.user:
                    self.message_post(body=msg)                
        
        return super().write(vals)
    
class AccountFollowupLine(models.Model):
    _name = 'account_followup.followup.line'
    _inherit = ['account_followup.followup.line', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    delay = fields.Integer(tracking=True)
    send_email = fields.Boolean(tracking=True)
    send_sms = fields.Boolean(tracking=True)
    mail_template_id = fields.Many2one(tracking=True)
    join_invoices = fields.Boolean(tracking=True)
    create_activity = fields.Boolean(tracking=True)
    
    
class AccountReconcile(models.Model):
    _inherit = 'account.reconcile.model'
    
    name=fields.Char(tracking=True)
    match_journal_ids = fields.Many2many(tracking=True)
    
    
class AccountAccount(models.Model):
    _inherit = 'account.account'

    tax_ids = fields.Many2many(tracking=True)
    allowed_journal_ids = fields.Many2many(tracking=True)
    
class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    description = fields.Char(tracking=True)
    active = fields.Boolean(tracking=True)
    tax_scope = fields.Selection(tracking=True)
    
class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    
    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)
    y_name_sequence_id = fields.Many2one(tracking=True)
    y_refund_sequence_id = fields.Many2one(tracking=True)
    y_ceiling_limit = fields.Boolean(tracking=True)
    y_ceiling_limit_value = fields.Float(tracking=True)
    type = fields.Selection(tracking=True)
    account_control_ids = fields.Many2many(tracking=True)
    default_account_id = fields.Many2one(tracking=True)
    
    restrict_mode_hash_table = fields.Boolean(tracking=True)

    invoice_reference_type = fields.Selection(tracking=True)
    invoice_reference_model = fields.Selection(tracking=True)

    #groups_id = fields.Many2many('res.groups', 'account_journal_group_rel', 'journal_id', 'group_id', string='Groups')
    currency_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)

    refund_sequence = fields.Boolean(tracking=True)
    
    profit_account_id = fields.Many2one(tracking=True)
    loss_account_id = fields.Many2one(tracking=True)
    sale_activity_type_id = fields.Many2one(tracking=True)
    sale_activity_user_id = fields.Many2one(tracking=True)
    
    
class AccountCurrency(models.Model):
    _name = 'res.currency'
    _inherit = ['res.currency', 'mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True)
    full_name = fields.Char(tracking=True)
    active = fields.Boolean(tracking=True)
    symbol = fields.Char(tracking=True)
    currency_unit_label = fields.Char(tracking=True)
    currency_subunit_label = fields.Char(tracking=True)
    rounding = fields.Float(tracking=True)
    decimal_places = fields.Integer(tracking=True)
    position = fields.Selection(tracking=True)
    
    
    
    def write(self,vals):
        new_dist = []
        if vals.get('rate_ids'):
            new_list = []
            for list1 in vals.get('rate_ids'):
                if list1[-1] != False:
                    new_list.append(list1)
                    rate_ids = self.rate_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
                    new_dist = []
                    for dicts in rate_ids:
                        for newval in new_list:
                            if not isinstance(newval[-1],int):
                                if newval[1] == dicts.id:
                                   
                                    if newval[-1].get('name'):
                                        new_name = newval[-1].get('name')
                                        new_dist.append('{}{} ---> {}'.format("Unit of Measure : ",dicts.name,new_name))
                                        
                                    if newval[-1].get('company_id'):
                                        new_name = newval[-1].get('company_id')
                                        new_dist.append('{}{} ---> {}'.format("Company : ",dicts.company_id,new_name))

                                    if newval[-1].get('company_rate'):
                                        new_name = newval[-1].get('company_rate')
                                        new_dist.append('{}{} ---> {}'.format("Unit Per INR : ",dicts.company_rate,new_name))

                                    if newval[-1].get('inverse_company_rate'):
                                        new_name = newval[-1].get('inverse_company_rate')
                                        new_dist.append('{}{} ---> {}'.format("INR Per Uni : ",dicts.inverse_company_rate,new_name))
                                    
                                    if newval[-1].get('rate'):
                                        new_name = newval[-1].get('rate')
                                        new_dist.append('{}{} ---> {}'.format("Rate : ",dicts.rate,new_name))

            if new_dist:
                msg = ', '.join(dic for dic in new_dist)
                if self.env.user:
                    self.message_post(body=msg)                
        
        return super().write(vals)
    
    
class AccountFiscalPosition(models.Model):
    _name = 'account.fiscal.position'
    _inherit = ['account.fiscal.position', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    company_id = fields.Many2one(tracking=True)
    auto_apply = fields.Boolean(tracking=True)
    vat_required = fields.Boolean(tracking=True)
    foreign_vat = fields.Char(tracking=True)
    country_group_id =fields.Many2one(tracking=True)
    country_id =fields.Many2one(tracking=True)
    state_ids = fields.Many2many(tracking=True)
    
    def write(self,vals):
        new_dist = []
        if vals.get('tax_ids'):
            new_list = []
            for list1 in vals.get('tax_ids'):
                if list1[-1] != False:
                    new_list.append(list1)
                    tax_ids = self.tax_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
                    new_dist = []
                    for dicts in tax_ids:
                        for newval in new_list:
                            if not isinstance(newval[-1],int):
                                if newval[1] == dicts.id:
                                   
                                    if newval[-1].get('tax_src_id'):
                                        # new_name = newval[-1].get('tax_src_id')
                                        new_name = self.env['account.tax'].browse(newval[-1].get('tax_src_id')).name     
                                        
                                        new_dist.append('{}{} ---> {}'.format("Tax on Product : ",dicts.tax_src_id.name,new_name))
                                        
                                    if newval[-1].get('tax_dest_id'):
                                        # new_name = newval[-1].get('tax_dest_id')
                                        new_name = self.env['account.tax'].browse(newval[-1].get('tax_dest_id')).name     
                                        
                                        new_dist.append('{}{} ---> {}'.format("Tax to Apply : ",dicts.tax_dest_id.name,new_name))

                                    
            if new_dist:
                msg = ', '.join(dic for dic in new_dist)
                if self.env.user:
                    self.message_post(body=msg)                
        
        return super().write(vals)
    
class AccountAccountTag(models.Model):
    _name = 'account.account.tag'
    _inherit = ['account.account.tag', 'mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True)
    applicability = fields.Selection(tracking=True)
    country_id =fields.Many2one(tracking=True)
    
class AccountGroups(models.Model):
    _name = 'account.group'
    _inherit = ['account.group', 'mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True)
    code_prefix_start = fields.Char(tracking=True)
    code_prefix_end =fields.Char(tracking=True)
    
class HsnList(models.Model):
    _name = 'hsn.san.list'
    _inherit = ['hsn.san.list', 'mail.thread', 'mail.activity.mixin']
    
    y_name = fields.Char(tracking=True)
    y_short_description = fields.Char(tracking=True)
    y_long_description = fields.Char(tracking=True)
    y_customer_tax_ids = fields.Many2many(tracking=True)
    y_vendor_tax_ids = fields.Many2many(tracking=True)
    y_product_id = fields.Many2one(tracking=True)
    
class PaymentMethod(models.Model):
    _name = 'payment.method'
    _inherit = ['payment.method', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)
    # primary_payment_method_id = 
    active = fields.Boolean(tracking=True)
    supported_country_ids = fields.Many2many(tracking=True)
    supported_currency_ids = fields.Many2many(tracking=True)
    
    support_tokenization = fields.Boolean(tracking=True)
    support_express_checkout = fields.Boolean(tracking=True)
    support_refund = fields.Selection(tracking=True)
    supported_country_ids =fields.Many2many(tracking=True)
    supported_currency_ids = fields.Many2many(tracking=True)
    provider_ids = fields.Many2many(tracking=True)
    
    # def write(self,vals):
    #     new_dist = []
    #     if vals.get('provider_ids'):
    #         new_list = []
    #         for list1 in vals.get('provider_ids'):
    #             if list1[-1] != False:
    #                 new_list.append(list1)
    #                 provider_ids = self.provider_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
    #                 new_dist = []
    #                 for dicts in provider_ids:
    #                     for newval in new_list:
    #                         if not isinstance(newval[-1],int):
    #                             if newval[1] == dicts.id:
    #                                 if newval[-1].get('name'):
    #                                     new_name = newval[-1].get('name')
    #                                     new_dist.append('{}{} ---> {}'.format("Name : ",dicts.name,new_name))
                                    
    #                                 if newval[-1].get('state') and dicts.state:
    #                                     new_uom_type = get_selection_label(self,'payment.provider','state',newval[-1].get('state'))
    #                                     old_uom_type = get_selection_label(self,'payment.provider','state',dicts.state)
    #                                     new_dist.append('{} for :{} ---> {}'.format("Type",old_uom_type,new_uom_type))    
                                    
                                    
    #         if new_dist:
    #             msg = ', '.join(dic for dic in new_dist)
    #             if self.env.user:
    #                 self.message_post(body=msg)                
        
    #     return super().write(vals)
    
class AccountAsset(models.Model):
    _inherit = 'account.asset'
    
    method = fields.Selection(tracking=True)
    # y_asset_code = fields.Char(tracking=True) 
    method_number = fields.Integer(tracking=True)
    method_period = fields.Selection(tracking=True)
    prorata_computation_type = fields.Selection(tracking=True)
    company_id = fields.Many2one(tracking=True)
    account_depreciation_id = fields.Many2one(tracking=True)
    account_depreciation_expense_id = fields.Many2one(tracking=True)
    journal_id = fields.Many2one(tracking=True)
    
class AccountCashRounding(models.Model):
    _name = 'account.cash.rounding'
    _inherit = ['account.cash.rounding', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    rounding = fields.Float(tracking=True)
    strategy = fields.Selection(tracking=True)
    profit_account_id = fields.Many2one(tracking=True)
    loss_account_id = fields.Many2one(tracking=True)
    rounding_method = fields.Selection(tracking=True)
    
    
class AccountBudget(models.Model):
    _name = 'account.budget.post'
    _inherit = ['account.budget.post', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    company_id = fields.Many2one(tracking=True)
    
    # account_ids
    
class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    plan_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    
    def write(self,vals):
        new_dist = []
        if vals.get('crossovered_budget_line'):
            new_list = []
            for list1 in vals.get('crossovered_budget_line'):
                if list1[-1] != False:
                    new_list.append(list1)
                    crossovered_budget_line = self.crossovered_budget_line.filtered(lambda x:x.id in [value[1] for value in new_list])
                    new_dist = []
                    for dicts in crossovered_budget_line:
                        for newval in new_list:
                            if not isinstance(newval[-1],int):
                                if newval[1] == dicts.id:
                                    if newval[-1].get('crossovered_budget_id'):
                                        new_name = self.env['crossovered.budget'].browse(newval[-1].get('crossovered_budget_id')).name     
                                        new_dist.append('{}{} ---> {}'.format("Budget : ",dicts.crossovered_budget_id.name,new_name))
                                        
                                    if newval[-1].get('general_budget_id'):
                                        new_name = self.env['account.budget.post'].browse(newval[-1].get('general_budget_id')).name     
                                        new_dist.append('{}{} ---> {}'.format("Budgetary Position : ",dicts.general_budget_id.name,new_name))
                                        
                                    if newval[-1].get('planned_amount'):
                                        new_planned_amount = newval[-1].get('planned_amount')
                                        new_dist.append('{}{} ---> {}'.format("Planned Amount : ",dicts.planned_amount,new_planned_amount))                 
                                    
            if new_dist:
                msg = ', '.join(dic for dic in new_dist)
                if self.env.user:
                    self.message_post(body=msg)                
        
        return super().write(vals)
    
class AccountAnalyticPlan(models.Model):
    _name = 'account.analytic.plan'
    _inherit = ['account.analytic.plan', 'mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True)
    parent_id = fields.Many2one(tracking=True)
    default_applicability = fields.Selection(tracking=True)
    y_business_unit = fields.Boolean(tracking=True)
    
    def write(self,vals):
        new_dist = []
        if vals.get('applicability_ids'):
            new_list = []
            for list1 in vals.get('applicability_ids'):
                if list1[-1] != False:
                    new_list.append(list1)
                    applicability_ids = self.applicability_ids.filtered(lambda x:x.id in [value[1] for value in new_list])
                    new_dist = []
                    for dicts in applicability_ids:
                        for newval in new_list:
                            if not isinstance(newval[-1],int):
                                if newval[1] == dicts.id:
                                    if newval[-1].get('business_domain') and dicts.business_domain:
                                            new_uom_type = get_selection_label(self,'account.analytic.applicability','business_domain',newval[-1].get('business_domain'))
                                            old_uom_type = get_selection_label(self,'account.analytic.applicability','business_domain',dicts.business_domain)
                                            new_dist.append('{}  :{} ---> {}'.format("Domain",old_uom_type,new_uom_type))
                                    
                                    if newval[-1].get('account_prefix'):
                                            new_planned_amount = newval[-1].get('account_prefix')
                                            new_dist.append('{}{} ---> {}'.format("Financial Accounts Prefix : ",dicts.account_prefix,new_planned_amount))                 
                                
                                    if newval[-1].get('product_categ_id'):
                                        new_name = self.env['product.category'].browse(newval[-1].get('product_categ_id')).name     
                                        new_dist.append('{}{} ---> {}'.format("Product Category : ",dicts.product_categ_id.name,new_name))
                                        
                                    if newval[-1].get('applicability') and dicts.applicability:
                                            new_uom_type = get_selection_label(self,'account.analytic.applicability','applicability',newval[-1].get('applicability'))
                                            old_uom_type = get_selection_label(self,'account.analytic.applicability','applicability',dicts.applicability)
                                            new_dist.append('{} for :{} ---> {}'.format("Applicability",old_uom_type,new_uom_type))
                                    
            if new_dist:
                msg = ', '.join(dic for dic in new_dist)
                if self.env.user:
                    self.message_post(body=msg)                
        
        return super().write(vals)
    
    
class ResPartnerCategory(models.Model):
    _name = 'res.partner.category'
    _inherit = ['res.partner.category', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    color = fields.Integer(tracking=True)
    parent_id =fields.Many2one(tracking=True)
    active = fields.Boolean(tracking=True)
    
class ResCountry(models.Model):
    _name = 'res.country'
    _inherit = ['res.country', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    phone_code = fields.Integer(tracking=True)
    currency_id =fields.Many2one(tracking=True)
    code = fields.Char(tracking=True)
    vat_label = fields.Char(tracking=True)
    zip_required = fields.Boolean(tracking=True)
    state_required = fields.Boolean(tracking=True)
    
class ResCountryGroup(models.Model):
    _name = 'res.country.group'
    _inherit = ['res.country.group', 'mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    country_ids = fields.Many2many(tracking=True)
    
class ResBank(models.Model):
    _name = 'res.bank'
    _inherit = ['res.bank', 'mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True)
    bic = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    state = fields.Many2one(tracking=True)
    zip = fields.Char(tracking=True)
    country = fields.Many2one(tracking=True)
    phone = fields.Char(tracking=True)
    # eamil = fields.Char(tracking=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


    
    
    
    
    
    
    
    
    
    
 