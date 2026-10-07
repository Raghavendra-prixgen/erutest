# -*- coding: utf-8 -*-
{
    'name': "odooe11",

    'summary': """
        This app enables multiple taxes to be selected in place of a single fiscal position
         """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    
    'website': "https://www.prixgen.com",

    'category': '',
    'version': '17.0.4.8',
    'license': 'LGPL-3',
    'origin': "Project Specific",
    'module_type': 'official',

    'depends': ['base','account','sale','account_accountant', 'stock', 'odoo_e_14_b','odoo_e_10_b','stock','odoo_e_08_b','product','purchase'],

    'data': [
          'security/ir.model.access.csv',
          'views/models_view.xml',
          "wizard/purchase.xml",
       
    ],
}
