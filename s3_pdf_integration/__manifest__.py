
{
    'name': "S3 PDF Integration for Log Notes",

    'summary': """
    Automatically upload PDFs to AWS S3 and enable preview
        """,

    'description': """
    This module automatically uploads PDF attachments from log notes to AWS S3
        and provides hover preview functionality by fetching data from S3.
        
        Features:
        - Automatic PDF upload to S3 when added to log notes
        - Hover preview functionality using presigned URLs
        - Secure access with temporary URLs (1 hour expiry)
        - Error handling and logging
        - Visual indicators for S3-stored attachments
       
    """,
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'module_type':'official',
    'license': 'LGPL-3',
    'App Origin': 'Base',

    'category': 'Inventory',
    'version': '17.0.1.9',
    'external_dependencies': {
        'python': ['boto3'],
    },

    'depends': ['base', 'mail'],
    'data': [
        'data/system_parameters.xml',
        'views/mail_message_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            's3_pdf_integration/static/src/js/pdf_preview.js',
        ],
    },
     'installable': True,
    'auto_install': False,
    'application': False,

    
}


