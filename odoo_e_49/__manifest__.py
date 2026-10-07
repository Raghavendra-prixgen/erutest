# -*- coding: utf-8 -*-
{
    'name': "odoo_e_49",

    'summary': """
        Inventory Detailed Summary""",

    'description': """
        Inventory Detailed Summary
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'module_type':'official',
    'license': 'LGPL-3',
    'App Origin': 'Base',

    'category': 'Inventory',
    'version': '17.0.0.3',

    'depends': ['base','product','stock','stock_account','stock_landed_costs'],

    'data': [
        'security/ir.model.access.csv',

        'views/views.xml',
    ],
}
