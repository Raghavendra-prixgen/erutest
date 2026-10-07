# -*- coding : utf-8 -*-
{
    'name': "Odooe46",

    'summary': """  
        Custom Aged Receivable Report and Custom Partner Ledger""",

    'description': """
        Custom Aged Receivable Report and Custom Partner Ledger
    """,
    'module_type':'official',
    'license': 'LGPL-3',

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'app origin' : "Project Specific",

    'category': 'Customization',
    'version': '17.0.0.2',

    'depends': ['account','base','account_reports'],

    'data': [
        'security/ir.model.access.csv',
        'data/aged_payable_view.xml',
        'data/aged_payable_menu.xml',
        'data/aged_receivable_view.xml',
        'data/aged_receivable_menu.xml',
        'data/partner_leadger_view.xml',
        'data/partner_ledger_menu.xml',


    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
