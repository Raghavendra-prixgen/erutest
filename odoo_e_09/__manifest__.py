# -*- coding: utf-8 -*-
{
    'name': "odooe09",

    'summary': """
        odooe09
         """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'module_type':'official',
    'category': '',
    'version': '17.0.1.6',
    'license': 'LGPL-3',
    'origin': "Project Specific",
    'depends': ['base','account','odoo_e_11','purchase','account_edi','odoo_e_14_b'],

    'data': [
        'views/header.xml',
        'report/commercial_invoice.xml',
    ],
    'installable': True,
    'application': False,
}
