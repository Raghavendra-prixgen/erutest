# -*- coding : utf-8 -*-
{
    'name': "Custom Aged Payable Report",

    'summary': """  
        Custom Aged Payable Report""",

    'description': """
        Custom Aged Payable Report
    """,
    'module_type':'official',
    'license': 'LGPL-3',

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'app origin' : "Project Specific",

    'category': 'Customization',
    'version': '17.0.0.1',

    'depends': ['account','base','account_reports'],

    'data': [
        'security/ir.model.access.csv',
        'data/view.xml',
        'data/aged_payable_menu.xml',


    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
