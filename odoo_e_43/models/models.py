# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import re


class RespartnerSignup(models.Model):
    _inherit = 'res.partner'

    def _compute_signup_url(self):
        result = self.sudo()._get_signup_url_for_action()

        for partner in self:
            if any(u._is_internal() for u in partner.user_ids if u != self.env.user):
                self.env['res.users'].check_access_rights('write')
            if any(u.has_group('base.group_portal') for u in partner.user_ids if u != self.env.user):
                self.env['res.partner'].check_access_rights('write')
   
            partner.signup_url = result.get(partner.id, False)


            signup_url = result.get(partner.id, False)
            if signup_url:
               
                signup_url = re.sub(r'http://[^/]+/', 'http://erp.eruvaka.com/', signup_url)
            partner.signup_url = signup_url



    