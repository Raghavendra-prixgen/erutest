import boto3
import base64
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from PIL import Image
import io
import unicodedata

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    s3_url = fields.Char('S3 URL', readonly=True)
    s3_key = fields.Char('S3 Key', readonly=True)
    is_s3_stored = fields.Boolean('Stored in S3', default=False)
    
    # Define supported file extensions for S3 storage
    S3_SUPPORTED_EXTENSIONS = [
        # Documents
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx','eml','msg',
        # Text files
        'txt', 'csv', 'json', 'xml', 'log',
        # Images
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',

        # video
        'mp4','webm','mov',

        #other files
        'zip','7z','rar','step','xps','step',

        'tif', 'tiff',
    ]
    
    # MIME type mappings
    MIME_TYPES = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'txt': 'text/plain',
        'csv': 'text/csv',
        'json': 'application/json',
        'xml': 'application/xml',
        'log': 'text/plain',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        'svg': 'image/svg+xml',
        'tif': 'image/tiff',
        'tiff': 'image/tiff',
    }

    def _safe_content_disposition(self, disposition_type, filename):
        """
        Returns a Content-Disposition value that is safe for S3 (ISO-8859-1 headers).
        Uses RFC 5987 encoding for non-ASCII filenames.
        """
        import urllib.parse
        try:
            filename.encode('iso-8859-1')
            # Pure ASCII/Latin-1 — safe to use directly
            return f'{disposition_type}; filename="{filename}"'
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Has non-Latin-1 chars — use RFC 5987 encoding
            encoded = urllib.parse.quote(filename, safe='')
            ascii_fallback = filename.encode('ascii', 'ignore').decode('ascii') or 'file'
            return f"{disposition_type}; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded}"


    # def _to_ascii(self, value):
    #     if not value:
    #         return ''
    #     return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')

    def _to_ascii(self, value):
        if not value:
            return ''
        
        import re
        value = unicodedata.normalize('NFKD', value)
        value = value.replace('\u00A0', ' ')  # remove non-breaking spaces
        value = value.encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'\s+', ' ', value)  # remove extra spaces
        return value.strip()
    
    def _get_s3_client(self):
        """Initialize and return S3 client"""
        try:
            return boto3.client(
                's3',
                aws_access_key_id=self.env['ir.config_parameter'].sudo().get_param('aws.access_key_id'),
                aws_secret_access_key=self.env['ir.config_parameter'].sudo().get_param('aws.secret_access_key'),
                region_name=self.env['ir.config_parameter'].sudo().get_param('aws.region', 'us-east-1')
            )
        except Exception as e:
            _logger.error(f"Failed to initialize S3 client: {e}")
            raise ValidationError("AWS S3 configuration error. Please check system parameters.")
    
    def _get_s3_bucket(self):
        """Get S3 bucket name from system parameters"""
        bucket = self.env['ir.config_parameter'].sudo().get_param('aws.s3_bucket')
        if not bucket:
            raise ValidationError("S3 bucket not configured in system parameters.")
        return bucket
    
    def _is_supported_for_s3(self, filename):
        """Check if file extension is supported for S3 storage"""
        if not filename:
            return False
    
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return extension in self.S3_SUPPORTED_EXTENSIONS
    
    def _get_content_type(self, filename):
        """Get content type based on file extension"""
        if not filename:
            return 'application/octet-stream'
        
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return self.MIME_TYPES.get(extension, 'application/octet-stream')


    @api.model_create_multi
    def create(self, vals_list):
        """Override create to push supported files to S3"""
        attachments = super(IrAttachment, self).create(vals_list)
        
        for attachment in attachments:
            # Check if this file should be stored in S3
            if (attachment.name and 
                self._is_supported_for_s3(attachment.name) and 
                attachment.datas and attachment.res_model == 'sale.document.notification'):
                try:
                    _logger.info(f"Attempting S3 upload for: {attachment.name}, mimetype: {attachment.mimetype}")
                    attachment._upload_to_s3()
                except Exception as e:
                    _logger.error(f"Failed to upload file to S3: {e}")
        
        return attachments
    
    def _upload_to_s3(self):
        """Upload file to S3 bucket"""
        if not self.datas:
            return
            
        bucket_name = self._get_s3_bucket()
        
        # Generate S3 key with proper structure
        # s3_key = f"odoo-attachments/{self.res_model}/{self.res_id}/{self.id}-{self.name}"


        clean_name = self._to_ascii(self.name).replace(' ', '_')

        s3_key = f"odoo-attachments/{self.res_model}/{self.res_id}/{self.id}-{clean_name}"

        # content_disposition = self._safe_content_disposition(
        #     'attachment', clean_name
        # )
        
        try:
            # Decode base64 data
            
            file_data = base64.b64decode(self.datas)
            extension = self.name.lower().split('.')[-1]

            # 🔥 AUTO CONVERT TIFF → PNG
            if extension in ['tif', 'tiff']:
                try:
                    image = Image.open(io.BytesIO(file_data))

                    # Handle multi-page TIFF → first page
                    if hasattr(image, "n_frames") and image.n_frames > 1:
                        image.seek(0)

                    image = image.convert("RGB")

                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")

                    file_data = buffer.getvalue()
                    self.name = self.name.rsplit('.', 1)[0] + '.png'

                    _logger.info(f"Converted TIFF to PNG for preview: {self.name}")

                except Exception as e:
                    _logger.error(f"TIFF conversion failed: {e}")





            s3_client = boto3.client('s3')
            
            # Get appropriate content type
            content_type = self._get_content_type(self.name)
            
            # Determine content disposition based on file type
            extension = self.name.lower().split('.')[-1] if '.' in self.name else ''
            if extension in ['pdf', 'txt', 'csv', 'json', 'xml', 'log', 
                           'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg','tiff','tif']:
                content_disposition = self._safe_content_disposition('inline', clean_name)

            else:
                content_disposition = self._safe_content_disposition('attachment', clean_name)
            
            # Upload to S3 with proper metadata
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type,
                ContentDisposition=content_disposition,
                Metadata={
                        'odoo_attachment_id': str(self.id),
                        'original_name': self._to_ascii(self.name),
                        'res_model': self._to_ascii(self.res_model or ''),
                        'res_id': str(self.res_id or ''),
                        'file_extension': extension
                    }
            )
            
            # Generate S3 URL
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
            
            # Update attachment record
            self.write({
                's3_url': s3_url,
                'datas': False,
                's3_key': s3_key,
                'is_s3_stored': True,
                'mimetype': content_type  # Update mimetype if needed
            })
            
            _logger.info(f"Successfully uploaded {self.name} to S3: {s3_url}")
            
        except Exception as e:
            _logger.error(f"S3 upload failed for attachment {self.id}: {e}")
            raise ValidationError(f"Failed to upload to S3: {str(e)}")
    
    def get_s3_preview_url(self):
        """Generate presigned URL for file preview"""
        if not self.is_s3_stored or not self.s3_key:
            return None
            
        try:
            s3_client = boto3.client('s3')
            bucket_name = self._get_s3_bucket()
            
            # Get file extension
            extension = self.name.lower().split('.')[-1] if '.' in self.name else ''
            content_type = self._get_content_type(self.name)
            
            # Determine response parameters based on file type
            response_params = {
                'Bucket': bucket_name,
                'Key': self.s3_key,
                'ResponseContentType': content_type,
            }

            
            # Set inline disposition for previewable files
            if extension in ['pdf', 'txt', 'csv', 'json', 'xml', 'log',
                           'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',
                           'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
                response_params['ResponseContentDisposition'] = self._safe_content_disposition('inline', self.name)
            else:
                response_params['ResponseContentDisposition'] = self._safe_content_disposition('attachment', self.name)
            
            # Generate presigned URL (valid for 1 hour)
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params=response_params,
                ExpiresIn=3600  # 1 hour
            )
            
            return presigned_url
            
        except Exception as e:
            _logger.error(f"Failed to generate presigned URL for attachment {self.id}: {e}")
            return None
    
    def action_retry_s3_upload(self):
        """Manual action to retry S3 upload for supported file types"""
        for attachment in self:
            print(self._is_supported_for_s3(attachment.name),2222222222222222333333)
            if not attachment.is_s3_stored and self._is_supported_for_s3(attachment.name):
                try:
                    attachment._upload_to_s3()
                except Exception as e:
                    raise ValidationError(f"Failed to upload {attachment.name}: {str(e)}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'S3 upload completed successfully',
                'type': 'success'
            }
        }
    
    def action_view_s3_preview(self):
        """Action to view file preview from S3"""
        self.ensure_one()
        
        if not self.is_s3_stored:
            raise ValidationError("This file is not stored in S3")
        
        presigned_url = self.get_s3_preview_url()
        if not presigned_url:
            raise ValidationError("Failed to generate preview URL")
        
        return {
            'type': 'ir.actions.act_url',
            'url': presigned_url,
            'target': 'new',
        }