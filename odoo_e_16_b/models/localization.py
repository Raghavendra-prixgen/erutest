from odoo import models, fields, api, _,exceptions

class ResCompany(models.Model):
    _inherit = "res.company"

    # y_tan_no = fields.Char(string="T.A.N.No")
    y_factory_number = fields.Char(string= "Factories Act. Regd. No.")
    y_company_status = fields.Selection([
                                        ('Pulic',"Public Limited Co."),
                                        ('private',"Private Limited Co."),
                                        ('other',"Others"),
                                        ('gov',"Goverment"),
                                        ('inv_pro',"Individual/Proprietary"),
                                        ('reg',"Register Trust"),
                                        ('partnership',"Partnership"),
                                        ('society',"Society/Co-op Society")],string="Company Status")
    y_msme_code = fields.Char(string="MSME Code")

    y_is_indian_company = fields.Boolean(string="Is Company")
    y_ccc_no = fields.Char(string="CCC No")
    y_ce_range = fields.Char(string="CE Range")
    y_ecc_number = fields.Char(string="ECC No.")
    y_ce_division = fields.Char(string="CE Division")
    y_tan_no = fields.Char(string="Tan No")
    y_tcan_no = fields.Char(string="T.C.A.N No.")
    y_circle_no = fields.Integer(string="Circle No")
    y_assignes_officer = fields.Char(string="Assignes Officer")
    y_ward_number = fields.Char(string="Ward Number")
        

    @api.onchange('country_id')
    def check_company_id(self):
        for rec in self:
            if self.country_id.name == 'India':
                rec.y_is_indian_company = True
            else:
                rec.y_is_indian_company = False

