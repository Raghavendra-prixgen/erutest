from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class S3PreviewController(http.Controller):
    
    @http.route('/web/s3_preview/<int:attachment_id>', type='http', auth='user')
    def s3_preview(self, attachment_id, **kwargs):
        """Controller to serve S3 file preview"""
        try:
            _logger.info(f"S3 preview requested for attachment ID: {attachment_id}")
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
            
            if not attachment.exists():
                _logger.warning(f"Attachment {attachment_id} not found")
                return request.not_found("Attachment not found")
            
            if not attachment.is_s3_stored:
                _logger.warning(f"Attachment {attachment_id} not stored in S3")
                return request.not_found("Attachment not stored in S3")
            
            presigned_url = attachment.get_s3_preview_url()
            if not presigned_url:
                _logger.error(f"Failed to generate presigned URL for attachment {attachment_id}")
                return request.not_found("Failed to generate preview URL")
            
            # Redirect to S3 presigned URL
            return request.redirect(presigned_url)
            
        except Exception as e:
            _logger.error(f"S3 preview error for attachment {attachment_id}: {e}", exc_info=True)
            return request.not_found(str(e))
    
    @http.route('/web/s3_preview_data/<int:attachment_id>', type='json', auth='user')
    def s3_preview_data(self, attachment_id, **kwargs):
        """Get S3 preview data for JavaScript"""
        try:
            _logger.info(f"=== S3 preview data requested for attachment ID: {attachment_id} ===")
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
            
            if not attachment.exists():
                _logger.warning(f"Attachment {attachment_id} not found")
                return {
                    'success': False,
                    'error': 'Attachment not found'
                }
            
            _logger.info(f"Attachment details:")
            _logger.info(f"  - Name: {attachment.name}")
            _logger.info(f"  - Mimetype: {attachment.mimetype}")
            _logger.info(f"  - Is S3 Stored: {attachment.is_s3_stored}")
            _logger.info(f"  - S3 Key: {attachment.s3_key}")
            _logger.info(f"  - S3 URL: {attachment.s3_url}")
            _logger.info(f"  - Has datas: {bool(attachment.datas)}")
            
            # If not stored in S3, try to upload it
            if not attachment.is_s3_stored:
                _logger.info(f"Attachment not in S3, checking if it can be uploaded...")
                
                if attachment.datas and attachment.name:
                    # Check if it's a supported file type
                    if attachment._is_supported_for_s3(attachment.name):
                        _logger.info(f"File type supported, attempting upload to S3...")
                        try:
                            attachment._upload_to_s3()
                            _logger.info(f"Successfully uploaded to S3")
                        except Exception as upload_error:
                            _logger.error(f"Failed to upload to S3: {upload_error}", exc_info=True)
                            return {
                                'success': False,
                                'error': f'Failed to upload to S3: {str(upload_error)}'
                            }
                    else:
                        _logger.warning(f"File type not supported for S3 storage")
                        return {
                            'success': False,
                            'error': 'File type not supported for preview'
                        }
                else:
                    _logger.warning(f"Attachment has no data or name")
                    return {
                        'success': False,
                        'error': 'Attachment has no data'
                    }
            
            # Generate presigned URL
            _logger.info(f"Generating presigned URL...")
            presigned_url = attachment.get_s3_preview_url()
            
            if not presigned_url:
                _logger.error(f"Failed to generate presigned URL")
                return {
                    'success': False,
                    'error': 'Failed to generate preview URL'
                }
            
            _logger.info(f"Successfully generated presigned URL: {presigned_url[:100]}...")
            
            return {
                'success': True,
                'preview_url': presigned_url,
                'filename': attachment.name,
                'mimetype': attachment.mimetype,
                's3_key': attachment.s3_key,
                's3_url': attachment.s3_url
            }
            
        except Exception as e:
            _logger.error(f"S3 preview data error for attachment {attachment_id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }
    
    @http.route('/web/s3_debug/<int:attachment_id>', type='json', auth='user')
    def s3_debug(self, attachment_id, **kwargs):
        """Debug endpoint to check attachment status"""
        try:
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
            
            if not attachment.exists():
                return {'error': 'Attachment not found'}
            
            return {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'is_s3_stored': attachment.is_s3_stored,
                's3_key': attachment.s3_key,
                's3_url': attachment.s3_url,
                'has_datas': bool(attachment.datas),
                'datas_length': len(attachment.datas) if attachment.datas else 0,
                'res_model': attachment.res_model,
                'res_id': attachment.res_id,
                'store_fname': attachment.store_fname,
            }
        except Exception as e:
            _logger.error(f"Debug error: {e}", exc_info=True)
            return {'error': str(e)}
    
    @http.route('/web/s3_proxy/<int:attachment_id>', type='http', auth='user')
    def s3_proxy(self, attachment_id, **kwargs):
        """Proxy endpoint to fetch S3 files and avoid CORS issues"""
        try:
            _logger.info(f"S3 proxy requested for attachment ID: {attachment_id}")
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
            
            if not attachment.exists():
                _logger.warning(f"Attachment {attachment_id} not found")
                return request.not_found("Attachment not found")
            
            if not attachment.is_s3_stored:
                _logger.warning(f"Attachment {attachment_id} not stored in S3")
                return request.not_found("Attachment not stored in S3")
            
            # Get presigned URL
            presigned_url = attachment.get_s3_preview_url()
            if not presigned_url:
                _logger.error(f"Failed to generate presigned URL for attachment {attachment_id}")
                return request.not_found("Failed to generate preview URL")
            
            # Fetch content from S3
            import requests
            response = requests.get(presigned_url, timeout=30)
            response.raise_for_status()
            
            # Get content type
            extension = attachment.name.lower().split('.')[-1] if '.' in attachment.name else ''
            content_type = attachment._get_content_type(attachment.name)
            
            # Return the content with appropriate headers
            return request.make_response(
                response.content,
                headers=[
                    ('Content-Type', content_type or 'image/tiff'),
                    ('Content-Disposition', f'inline; filename="{attachment.name}"'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type'),
                ]
            )
            
        except Exception as e:
            _logger.error(f"S3 proxy error for attachment {attachment_id}: {e}", exc_info=True)
            return request.not_found(str(e))