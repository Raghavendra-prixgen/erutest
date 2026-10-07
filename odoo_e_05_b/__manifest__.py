# -*- coding: utf-8 -*-
{
    'name': "odooe05b",

    'summary': """
        Sequence Customization and Ceiling Limit on Accounting""",

    'description': """
        Included Functionalities -
            1) Sequence field in Journal masters picked by Sale Invoices for custom sequence
            2) Override Sequence Mixin to avoid date validation error
            3) Journal wise Ceiling limit
    """,

    'module_type':'official',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    
    'category': 'Account',
    'App Origin': 'Base',
    'version': '17.0.0.6',
    'license': 'LGPL-3',

    'depends': ['base','account'],
    'data': [
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/res_config_settings.xml'
    ],

    'auto_install': False,
    'installable': True,
}

