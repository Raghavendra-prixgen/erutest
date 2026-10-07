# -*- coding: utf-8 -*-
{
    'name': "odooe08b",

    'summary': """
        This module is used for transferring materials between one branch to another branch.
        """,

    'description': """
        This module is used for transferring materials between one branch to another branch.
    """,
    'module_type':'official',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',

    
    'category': 'Uncategorized',
    'App origin': 'Project Specific',

    'version': '17.0.2.7',
    'license': 'LGPL-3',
   
    'depends': ['base','stock','account','stock_account','stock_landed_costs','l10n_in',],

    'data': [
        'data/btb_sequence.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/branch_to_branch_config.xml',
        'views/branch_to_branch.xml',
        'views/stock.xml',
        'views/stock_location.xml',
    ],
}


