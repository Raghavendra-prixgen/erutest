# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    y_provident_fund = fields.Char(string="PF No.",store=True)
    y_universal_account_number = fields.Char(string="PF UAN",store=True)
    y_esi_number = fields.Char(string="ESIC No.",store=True)
    y_pan_no = fields.Char(string="PAN No.",store=True)
    y_aadhaar_number = fields.Char(string="Aadhaar No.")

class CountryStateTin(models.Model):
    _inherit = 'res.country.state'

    y_l10n_in_tin = fields.Char(string="TIN Number", size=2, help="TIN number-first two digits")

class Partner(models.Model):
    _inherit = 'res.partner'

    y_is_indian_company = fields.Boolean(string="Is Indian Company",compute="check_company_id")
    l10n_in_pan = fields.Char(compute='_get_pan_no',store=True,inverse='_set_pan_no')

    @api.depends('company_id')
    def check_company_id(self):
        for rec in self:
            if self.env.company.country_id.name == 'India':
                rec.y_is_indian_company = True
            else:
                rec.y_is_indian_company = False


    @api.constrains('l10n_in_pan')
    def _check_pan_number(self):
        for rec in self:
            if rec.l10n_in_pan and len(rec.l10n_in_pan) != 10:
                raise ValidationError(_("The PAN number must be 10 alphanumeric character"))
        return True
    

    @api.constrains('vat')
    def _check_pan_vat(self):
        for rec in self:
            if rec.vat and len(rec.vat) != 15:
                raise ValidationError(_("The GST number must be 15 alphanumeric character"))
        return True


    # to set the limit of pan no
    @api.depends('vat')
    def _get_pan_no(self):
        for r in self:
            if r.vat:
                r.l10n_in_pan = r.vat[2:12]


    # pan num to editable
    def _set_pan_no(self):
        for r in self:
            r.l10n_in_pan = r.l10n_in_pan
            
    @api.onchange('vat','state_id')
    def validate_vat(self):
        if self.state_id.country_id.id == 104 and self.vat:
            vat = self.vat
            sc = self.env['res.country.state'].search([('id','=',self.state_id.id)]).y_l10n_in_tin
            if vat[:2] != sc:
                raise ValidationError(_("GST Code Not Matched"))




    