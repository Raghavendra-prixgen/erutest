from odoo import models, fields, api, _,exceptions
import datetime
from datetime import date
from datetime import timedelta
import math
from odoo.exceptions import ValidationError
import json

class ResCompany(models.Model):
    _inherit = "res.company"

    tan_no = fields.Char(string="T.A.N.No")
    factory_number = fields.Char(string= "Factories Act. Regd. No.")
    company_status = fields.Selection([
                                        ('Pulic',"Public Limited Co."),
                                        ('private',"Private Limited Co."),
                                        ('other',"Others"),
                                        ('gov',"Goverment"),
                                        ('inv_pro',"Individual/Proprietary"),
                                        ('reg',"Register Trust"),
                                        ('partnership',"Partnership"),
                                        ('society',"Society/Co-op Society")],string="Company Status")
    msme_code = fields.Char(string="MSME Code")
    y_is_indian_company = fields.Boolean()
        

    @api.onchange('country_id')
    def check_company_id(self):
        for rec in self:
            if self.country_id.name == 'India':
                rec.y_is_indian_company = True
            else:
                rec.y_is_indian_company = False


class ResPartner(models.Model):
    _inherit ="res.partner"

    y_msme_registered = fields.Boolean(string="MSME Registered")
    y_registration_number = fields.Char(string="MSME Reg No.",size=19)
    y_is_micro_or_small_enterprise = fields.Boolean(string="MSME Micro",copy=False)
    y_msme_small = fields.Boolean(string="MSME Small",copy=False)
    y_msme_medium = fields.Boolean(string="MSME Medium",copy=False)
    y_is_aggrement_msme = fields.Boolean(string="Is Agreement")
    y_monthly_interest_rate = fields.Float(string="Monthly Interest Rate", digits=(12, 4))
    warning_bool = fields.Boolean(string="Warning Bool")
    y_msme_reg_date = fields.Date(string="MSME Reg Date")
    y_validity_period = fields.Char(default="1 Year" ,string="MSME Validity Period", readonly=True)
    y_expiry_date = fields.Date(string="MSME Expiry Date",compute="_compute_expiry_date",store=True)
    y_validity_days = fields.Char(string="MSME Validity Days",compute="_compute_validity_days",store=True)
    y_type_of_business = fields.Selection([
                                        ('trading',"Trading"),
                                        ('manufacturing',"Manufacturing"),
                                        ('service_provider',"Service Provider"),
                                        ],string="Type of Business",help="MSME Type of Business")





    @api.constrains('y_is_micro_or_small_enterprise','y_msme_small','y_msme_medium','y_registration_number')
    def check_msme_option(self):
                for rec in self:
                    if rec.y_msme_registered == True:
                        if rec.y_is_micro_or_small_enterprise == False and rec.y_msme_small == False and rec.y_msme_medium == False:
                            raise ValidationError("MSME category is mandatory")
                       
                    

    @api.constrains('y_registration_number')
    def _check_registration_number(self):
            for rec in self:
                if rec.y_msme_registered == True:
                    if len(rec.y_registration_number) != 19:
                        raise ValidationError("Registration number should be 19 digits")


    @api.depends('y_expiry_date')
    def _compute_validity_days(self):
        for rec in self:
            if rec.y_msme_registered == True and rec.y_expiry_date:
                days_remaining = (rec.y_expiry_date - date.today()).days
                rec.y_validity_days = f"{days_remaining} days"
            else:
                rec.y_validity_days = "0 days"


    @api.depends('y_msme_reg_date')
    def _compute_expiry_date(self):
        for rec in self:
            if rec.y_msme_registered == True and rec.y_msme_reg_date:
                rec.y_expiry_date = rec.y_msme_reg_date + timedelta(days=365)
            else:
                rec.y_expiry_date = False


    
    @api.constrains('y_msme_reg_date')
    def check_date(self):
        for rec in self:
            if rec.y_msme_registered == True:
                if rec.y_msme_reg_date:
                    if rec.y_msme_reg_date > date.today():
                        raise ValidationError(_("Registration Date cannot be greater than today's date."))
                else:
                    raise ValidationError(_("Registration date cannot be empty."))
                
                
    @api.onchange('y_is_micro_or_small_enterprise')
    def onchange_y_is_micro_or_small_enterprise(self):
        for rec in self:
            if rec.y_msme_registered == True and rec.y_is_micro_or_small_enterprise == True:
                rec.y_msme_small = False
                rec.y_msme_medium = False

    @api.onchange('y_msme_small')
    def onchange_y_msme_small(self):
        for rec in self:


            if rec.y_msme_registered == True and rec.y_msme_small == True:
                rec.y_is_micro_or_small_enterprise = False
                rec.y_msme_medium = False

    @api.onchange('y_msme_medium')
    def onchange_y_msme_medium(self):
        for rec in self:


            if rec.y_msme_registered == True and rec.y_msme_medium == True:
                rec.y_is_micro_or_small_enterprise = False
                rec.y_msme_small = False

    @api.onchange('l10n_in_gst_treatment')
    def popup_warning(self):
        for rec in self:
            if rec.l10n_in_gst_treatment == 'composition':
                rec.warning_bool = True

class AccountMoveMsme(models.Model):
    _inherit = "account.move"

    y_is_micro_or_small_enterprise = fields.Boolean(related="partner_id.y_is_micro_or_small_enterprise",string="Is Micro & Small Entp (Yes/No)")
    y_registration_number = fields.Char(related="partner_id.y_registration_number",string="MSME (Micro Small & Medium Enterprises) Reg No.")
    y_is_aggrement_msme = fields.Boolean(related="partner_id.y_is_aggrement_msme",string="Is Agreement")
    y_day_15_limit = fields.Date(string='15 days limit',compute="calculate_15dayslimit")
    y_date_as_po_agreed = fields.Date(string='Date As PO')
    y_date_as_per_agreed_terms = fields.Date(string='Date As Per Agreed Terms')
    y_date_of_payment = fields.Date(string='Date of Payment',default=fields.Date.context_today)
    y_delay_by_no_months = fields.Float(string="Delay by No of Mths",compute="action_y_delay_by_no_months")
    y_monthly_interest_rate = fields.Float(related="partner_id.y_monthly_interest_rate",string="Monthly Interest Rate", digits=(12, 4))
    y_interedted_amount = fields.Float(string="Interest Amount",compute="compute_compounded_amount")
    y_is_micro_yes_or_no = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is Micro & Small Entp (Yes/No)',compute="action_y_is_micro_or_small_enterprise")
    y_is_aggrement_msme_yes_or_no = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is Agreement',compute="action_y_is_aggrement_msme_yes_or_no")
    y_account_date_tooltip = fields.Char(compute="_compute_action_y_account_date_tooltip")
    y_amount_paid_tilldate =  fields.Monetary(compute="_compute_y_amount_paid_tilldate",store=True)
    y_payed_date = fields.Date(string="Paid date",compute="_compute_y_payed_date",store=True)
    y_days_from = fields.Integer(string="Days from Acceptance Date to as of today",compute="_compute_y_days_from",store=True)
    y_po = fields.Boolean(compute="_compute_y_payed_date")




    @api.depends('name','invoice_payments_widget',)
    def _compute_y_payed_date(self):
        for bill in self:

            bill.y_payed_date = False
           
            if bill.state == 'posted' and bill.invoice_payments_widget:
                payment_dict = bill.invoice_payments_widget
                # payment_dict = str(json.loads(bill.invoice_payments_widget))
                if payment_dict:
                    em_list = []
                    for record in payment_dict.get('content'):
                        em_list.append(record.get('date'))
                    bill.y_payed_date = max(em_list)

            bill.y_po =True



    @api.depends('invoice_date')
    def _compute_y_days_from(self):
        for record in self:
            if record.invoice_date:
                today = date.today()
                invoice_date = fields.Date.from_string(record.invoice_date)
                record.y_days_from = (today - invoice_date).days + 1
            else:
                record.y_days_from = 0

    @api.depends('y_is_micro_or_small_enterprise')
    def action_y_is_micro_or_small_enterprise(self):
        for rec in self:
            if rec.y_is_micro_or_small_enterprise == True:
                rec.y_is_micro_yes_or_no = 'yes'
            else:
                rec.y_is_micro_yes_or_no = 'no'

    @api.depends('y_is_aggrement_msme')
    def action_y_is_aggrement_msme_yes_or_no(self):
        for rec in self:
            if rec.y_is_aggrement_msme == True:
                rec.y_is_aggrement_msme_yes_or_no = 'yes'
            else:
                rec.y_is_aggrement_msme_yes_or_no = 'no'

    @api.depends('invoice_date_due')
    def calculate_15dayslimit(self):
        for rec in self:
            if rec.y_is_aggrement_msme_yes_or_no == 'no':
                rec.y_day_15_limit = rec.invoice_date + datetime.timedelta(days=15)
                rec.y_date_as_po_agreed = None
            else:
                rec.y_date_as_po_agreed = rec.invoice_date_due
                rec.y_day_15_limit = None
               
                if (rec.invoice_date_due - rec.invoice_date).days > 45:
                    rec.y_date_as_per_agreed_terms = rec.invoice_date + datetime.timedelta(days=45)

                else:
                    rec.y_date_as_per_agreed_terms = rec.invoice_date_due

    @api.depends('y_is_aggrement_msme_yes_or_no')
    def action_y_delay_by_no_months(self):
        for rec in self:
            if rec.y_is_aggrement_msme_yes_or_no == 'no':
                rec.y_delay_by_no_months = (rec.y_date_of_payment - rec.y_day_15_limit).days/30
            else:
                rec.y_delay_by_no_months = (rec.y_date_of_payment - rec.y_date_as_per_agreed_terms).days/30

    @api.depends('y_delay_by_no_months')
    def compute_compounded_amount(self):
        for rec in self:
            if rec.y_delay_by_no_months > 0:
                val=(1+(rec.y_monthly_interest_rate))
                comp_val = math.pow(val,rec.y_delay_by_no_months)
                rec.y_interedted_amount = (rec.amount_residual*comp_val)-rec.amount_residual

            else:
                rec.y_interedted_amount = 0


    @api.depends('move_type')
    def _compute_action_y_account_date_tooltip(self):
        for record in self:
            if record.move_type == 'in_invoice':
                record.y_account_date_tooltip = _(
                    "Acconting date Should be the GRN Date for MSME ")
            else:
                record.y_account_date_tooltip = ""


    @api.depends('amount_total', 'amount_residual')
    def _compute_y_amount_paid_tilldate(self):
        for record in self:

            record.y_amount_paid_tilldate = abs(record.amount_total - record.amount_residual)


class IndiaMsmeWiz(models.TransientModel):
    _name = 'india.msme.wiz'
    _description = 'India Msme Wizard'

    y_open_date = fields.Datetime(string='Start Date')
    y_close_date = fields.Datetime(string='End Date')
    
    
    @api.onchange('y_close_date')
    def _onchange_y_close_date(self):
        if self.y_close_date < self.y_open_date:
            raise ValidationError(_("""End Date should not be less than Start Date"""))

    def action_open_report(self):
        tree_view_id = self.env.ref('odoo_e_15_b.india_msme_report_tree_view').id

        return {
            'name': 'MSME Report',
            'view_mode': 'tree',
            'views': [[tree_view_id, 'tree']],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('company_id', '=', self.env.company.id),
            ('partner_id.y_msme_registered', '=', True),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', self.y_open_date),
            ('invoice_date', '<=', self.y_close_date),
            ('partner_id.y_msme_medium', '!=', True),
            ]


            }
