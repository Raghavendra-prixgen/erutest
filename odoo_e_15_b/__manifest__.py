# -*- coding: utf-8 -*-
{
    'name': "odooe15b",

    'summary': """  
        Indian Localization,
        MSME Basic""",

    'description': """
        Indian Localization
        GST Code Validations

        Instead of GST code, functionality is based on TIN Number which is same as GST Code
    """,
    'module_type':'official',
    'license': 'LGPL-3',

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Customization',
    'version': '17.0.0.5',

    'depends': ['hr','base','account_reports'],

    'data': [
        'security/ir.model.access.csv',

        # 'views/gst_code_validation_views.xml',
        'views/vendor_msme.xml',
        'views/msme_report.xml',
        # 'data/state_code.xml',
    ],
}
