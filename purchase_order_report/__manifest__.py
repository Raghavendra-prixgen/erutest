# -*- coding: utf-8 -*-
{
    'name': "Eruvaka Purchase Order Reports",

    'summary': """
        """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",

    'version': '17.0.0.6',
    'license': 'LGPL-3',
    'module_type':'official',
    'depends': ['base','purchase','web','custom_app_eruvaka','l10n_in','stock'],

    'data': [
        'reports/import_purchase_order_report.xml', 
        'reports/header_footer.xml', 
        'reports/header_footer_import.xml',
        'reports/purchase_order_report.xml',
        
    ],

    'auto_install': False,
    'installable': True,
    'application': False,
}
