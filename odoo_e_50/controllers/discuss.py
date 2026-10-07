
from odoo.exceptions import AccessError
from odoo.http import request
from odoo import _
from odoo.addons.mail.controllers.attachment import AttachmentController
from werkzeug.exceptions import NotFound

class DiscussController(AttachmentController):

    def mail_attachment_upload(self, ufile, thread_id, thread_model,
                               is_pending=False, **kwargs):
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
        except AccessError:
            attachmentData = {
                "error": _("You are not allowed to upload an attachment here.")}
        return request.make_json_response(attachmentData)
