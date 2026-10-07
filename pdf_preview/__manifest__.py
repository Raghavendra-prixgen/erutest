
{
    'name': 'PDF preview for Log Notes',
    'version': '17.0.0.1',
    'category': 'Document Management',
    'summary': 'Enable preview',
    'App origin':'Base',
    'description': """
        provides hover preview functionality by fetching data from S3.
                    """,
    'module_type':'official',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',    

    'depends': ['base', 'mail','web','upload_s3'],
    'external_dependencies': {
        'python': ['boto3'],
    },
    'data': [
        
    ],
    'assets': {
        'web.assets_backend': [
            'pdf_preview/static/src/js/pdf_preview.js',
        ],
    },
    
}

