# -*- coding: utf-8 -*-
{
    'name': "odooe16b",

    'summary': """  
        Indian Localization""",

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
    'origin': 'base',
    'version': '17.0.0.2',

    'depends': ['hr','base','l10n_in'],

    'data': [
        'security/ir.model.access.csv',
        'views/localization.xml',
        'views/gst_code_validation_views.xml',
        'views/hsn_san_list.xml',
    ],
}
