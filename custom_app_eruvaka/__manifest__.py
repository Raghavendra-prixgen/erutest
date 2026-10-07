# -*- coding: utf-8 -*-
{
    'name': "Custom Fields App Eruvaka",

    'summary': """
        This app enables multiple taxes to be selected in place of a single fiscal position
         """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': '',
    'version': '17.0.0.8',
    'license': 'LGPL-3',
    'origin': "Project Specific",
    'module_type': 'official',

    'depends': ['base','account','sale','account_accountant','export_imports', 'stock'],

    'data': [
          'views/models.xml',
          'security/ir.model.access.csv',
       
    ],
}
