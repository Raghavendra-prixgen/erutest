from odoo import models, fields, api


class ResConfigSettingsDis(models.TransientModel):
    _inherit ='res.config.settings'

    y_group_advance_request_id = fields.Boolean(string="Down Payment Request" ,implied_group='odoo_e_27_b.y_group_advance_request_id')



    def set_values(self):
        super(ResConfigSettingsDis,self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('odoo_e_27_b.y_group_advance_request_id',self.y_group_advance_request_id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsDis, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        res.update(y_group_advance_request_id = param.get_param('odoo_e_27_b.y_group_advance_request_id') or False)
        return res
    


class PurchaseConfig(models.Model):

    _name  = 'product.groups'
    _description = 'product_groups'

    _rec_name = "y_product_group"

    y_product_group = fields.Char(string="Purchase Group",store=True,tracking=True)

