
from odoo.exceptions import AccessError
from odoo.http import request
from odoo import _
from odoo.addons.mail.controllers.attachment import AttachmentController
from werkzeug.exceptions import NotFound
import io
import logging
import zipfile
import boto3
import re
from werkzeug.exceptions import NotFound
from datetime import datetime
import base64

from odoo import _, http
from odoo.exceptions import AccessError
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError

from odoo.tools import consteq
class DiscussController(AttachmentController):

    @http.route("/mail/attachment/upload", methods=["POST"], type="http", auth="public")
    
    def mail_attachment_upload(self, ufile, thread_id, thread_model, is_pending=False, **kwargs):

        thread = request.env[thread_model].search([("id", "=", thread_id)])
        if not thread:
            raise NotFound()
        channel_member = request.env['discuss.channel.member']
        limited_max_size = 10.0
        max_size = limited_max_size * 1024 * 1024
        if (thread_model == "discuss.channel" and not thread.allow_public_upload
                and not request.env.user._is_internal()):
            raise AccessError(
                _("You are not allowed to upload attachments on this channel."))
        vals = {
            "name": ufile.filename,
            "raw": ufile.read(),
            "res_id": int(thread_id),
            "res_model": thread_model,
        }
        if is_pending and is_pending != "false":
           
            vals.update(
                {
                    "res_id": 0,
                    "res_model": "mail.compose.message",
                }
            )
        if request.env.user.share:
            vals["access_token"] = request.env[
                "ir.attachment"]._generate_access_token()
        try:
          
            attachment = request.env["ir.attachment"].sudo().create(vals)
            attachment._post_add_create(**kwargs)
            attachmentData = attachment._attachment_format()[0]
            if attachment.access_token:
                attachmentData["accessToken"] = attachment.access_token
            if attachmentData['size'] > max_size:
                attachmentData = {'error': _('Attachment'
                                             ' size cannot exceed %s MB.'
                                             ) % limited_max_size}

                attachment.unlink()
            else:
                attachment._upload_to_s3()
                # bucket = request.env['ir.config_parameter'].sudo().get_param('upload_s3.s3_bucket')    
                # region = request.env['ir.config_parameter'].sudo().get_param('upload_s3.s3_region')
                # if bucket and region:                
                #     s3_client = boto3.client('s3')
                #     for rec in attachment:

                #         name = rec.name.replace(" ", "")
                #         name = re.sub('[^a-zA-Z0-9 \n\.]', '_', name)

                #         # if rec.res_model and rec.res_id:
                #         #     obj = self.env[rec.res_model].sudo().browse(rec.res_id)
                #         datetime_now = datetime.now()
                #         datetime_now = str(datetime_now).replace(" ", "")
                #         name = str(datetime_now) +'-'+name 
                #         rec.s3_attachment_name = name
                #         if rec.mimetype == 'application/pdf':
                #             s3_client.put_object(Body=base64.b64decode(rec.datas or b''), Bucket=bucket, Key=name,ContentType='application/pdf')
                #         else:
                #             s3_client.put_object(Body=base64.b64decode(rec.datas or b''), Bucket=bucket, Key=name)              
                #         url = f'https://{bucket}.s3.{region}.amazonaws.com/{name}'
                       
                #         # if rec.res_model and rec.res_id:
                #         #     obj = self.env[rec.res_model].sudo().browse(rec.res_id)
                #         #     if obj:
                #         #         obj.message_post(subject="Attachment URL:",body=_("Document %s is uploaded and URL: %s")% (rec.name,url))
                #         #         # res.url = url
                #         rec.s3_url = url
                #         rec.datas = False
        except AccessError:
            attachmentData = {
                "error": _("You are not allowed to upload an attachment here.")}
        return request.make_json_response(attachmentData)
