# -*- coding: utf-8 -*-
{
    'name': "Commercial Invoice",

    'summary': """
        Commercial Invoice
         """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'module_type':'official',
    'category': '',
    'version': '17.0.1.0',
    'license': 'LGPL-3',

    'depends': ['base','account','custom_app_eruvaka','purchase','account_edi','export_imports'],

    'data': [
        'views/header.xml',
        'report/commercial_invoice.xml',
    ],
    'installable': True,
    'application': False,
}
