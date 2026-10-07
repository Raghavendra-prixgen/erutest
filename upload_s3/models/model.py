# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019-2020 Eugene Molotov <https://it-projects.info/team/em230418>
import os

import boto3

from odoo import _, api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    s3_region = fields.Char()
    s3_bucket = fields.Char()
    

    def set_values(self):
        super(ResConfigSettings,self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('upload_s3.s3_region',self.s3_region)
        param.set_param('upload_s3.s3_bucket',self.s3_bucket)
        

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        res.update(s3_region = param.get_param('upload_s3.s3_region'))
        res.update(s3_bucket = param.get_param('upload_s3.s3_bucket'))
       
        return res