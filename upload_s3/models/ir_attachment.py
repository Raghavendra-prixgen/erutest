import logging
import os
import random
import time
import re

import boto3
from botocore.exceptions import ClientError

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo import api, fields, tools, models, _
import mimetypes
from odoo.tools.mimetypes import guess_mimetype

from odoo.http import request

_logger = logging.getLogger(__name__)

import boto3
import requests
from botocore import client
import base64
import hashlib
import io
import itertools
import logging
import mimetypes
import os
import re
import uuid

from collections import defaultdict
from PIL import Image

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
from odoo.tools import config, human_size, ustr, html_escape, ImageProcess, str2bool
from odoo.tools.mimetypes import guess_mimetype
from datetime import datetime
from odoo import api, models, _
from odoo.exceptions import UserError
import base64
import boto3
import re
from datetime import datetime

MAX_SIZE = 10 * 1024 * 1024  # 10MB


class MailMessageAttachment(models.Model):
    _inherit = "mail.message"

    attachment_id = fields.Integer(string="Attachment ID")




class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    s3_attachment_name = fields.Char()
    s3_url = fields.Char('S3 URL', readonly=True)


    # def unlink(self):
    #     for rec in self:
    #         name = rec.name.replace(" ", "")
    #         name = re.sub('[^a-zA-Z0-9 \n\.]', '_', name)

    #         # if rec.res_model and rec.res_id:
    #         #     obj = self.env[rec.res_model].sudo().browse(rec.res_id)
    #         name = rec.s3_attachment_name 
    #         s3_bucket = self.env['ir.config_parameter'].sudo().get_param('upload_s3.s3_bucket')
    #         if s3_bucket:
    #             s3_client = boto3.client('s3')
    #             response = s3_client.delete_object(Bucket=s3_bucket, Key=name)

    #             if response:
    #                 link_obj = self.env['mail.message'].search([('attachment_id','=',rec.id),('model','=',rec.res_model),('res_id','=',rec.res_id)])
    #                 if link_obj:
    #                     link_obj.unlink()

    #     return super().unlink()

    def update_attachments_to_s3(self):
        s3_client = boto3.client('s3')       
        s3_bucket = self.env['ir.config_parameter'].sudo().get_param('upload_s3.s3_bucket')        
        region = self.env['ir.config_parameter'].sudo().get_param('upload_s3.s3_region')        
        if s3_bucket and region:
            for rec in self:
                if not rec.res_field:

                    name = rec.name.replace(" ", "")
                    name = re.sub('[^a-zA-Z0-9 \n\.]', '_', name)

                    # if rec.res_model and rec.res_id:
                    #     obj = self.env[rec.res_model].sudo().browse(rec.res_id)
                    datetime_now = datetime.now()
                    datetime_now = str(datetime_now).replace(" ", "")
                    name = str(datetime_now) +'-'+name 

                    rec.s3_attachment_name = name

                    print(name)

                    if rec.mimetype == 'application/pdf':

                        s3_client.put_object(Body=base64.b64decode(rec.datas or b''), Bucket=s3_bucket, Key=name,ContentType='application/pdf')
                    else:
                        s3_client.put_object(Body=base64.b64decode(rec.datas or b''), Bucket=s3_bucket, Key=name)

                    url = f'https://{s3_bucket}.s3.{region}.amazonaws.com/{name}'
                    # if rec.res_model and rec.res_id:
                    #     obj = self.env[rec.res_model].sudo().browse(rec.res_id)

                    #     obj.message_post(subject="Attachment URL:",body=_("Document %s is uploaded and URL: %s")% (rec.name,url))

                        # res.url = url
                    rec.s3_url = url
                    rec.datas = False


    # @api.model_create_multi
    # def create(self,vals_list):       
    #     res = super().create(vals_list)
    #     if not res.res_field:
    #             # if res.file_size < 10000000:
    #             bucket = self.env['ir.config_parameter'].sudo().get_param('upload_s3.s3_bucket')    
    #             region = self.env['ir.config_parameter'].sudo().get_param('upload_s3.s3_region')
    #             if bucket and region:                
    #                 s3_client = boto3.client('s3')
    #                 for rec in res:
    #                     name = rec.name.replace(" ", "")
    #                     name = re.sub('[^a-zA-Z0-9 \n\.]', '_', name)

    #                     # if rec.res_model and rec.res_id:
    #                     #     obj = self.env[rec.res_model].sudo().browse(rec.res_id)
    #                     datetime_now = datetime.now()
    #                     datetime_now = str(datetime_now).replace(" ", "")
    #                     name = str(datetime_now) +'-'+name 
    #                     rec.s3_attachment_name = name
    #                     if rec.mimetype == 'application/pdf':
    #                         s3_client.put_object(Body=base64.b64decode(rec.datas or b''), Bucket=bucket, Key=name,ContentType='application/pdf')
    #                     else:
    #                         s3_client.put_object(Body=base64.b64decode(rec.datas or b''), Bucket=bucket, Key=name)              
    #                     url = f'https://{bucket}.s3.{region}.amazonaws.com/{name}'
                       
    #                     # if rec.res_model and rec.res_id:
    #                     #     obj = self.env[rec.res_model].sudo().browse(rec.res_id)
    #                     #     if obj:
    #                     #         obj.message_post(subject="Attachment URL:",body=_("Document %s is uploaded and URL: %s")% (rec.name,url))
    #                     #         # res.url = url
    #                     rec.s3_url = url
    #                     # rec.datas = False
    #         # else:
    #         #     raise UserError(_("File size should be within 10MB"))
    #     return res

   