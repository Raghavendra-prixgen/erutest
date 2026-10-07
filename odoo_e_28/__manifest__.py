# -*- coding: utf-8 -*-
{
    'name': "odooe28",

    'summary': """
        """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'origin': "Project Specific",
    'version': '17.0.1.9',
    'license': 'LGPL-3',
    'module_type':'official',
    'depends': ['base','purchase','web','odoo_e_11','l10n_in','stock'],

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
