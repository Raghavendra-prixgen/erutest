{
    'name': "Transaction Currency Balance",

    'summary': """  """,

    'description':"""
       """,
    
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',

    'company': 'Prixgen Tech Solutions Pvt. Ltd.',

    'website': 'https://www.prixgen.com', 

    'module_type':'official',   
    
    'category': 'Accounting',

    'version': '17.0.0.1',

    'App origin':'Base_17',

    'license': 'LGPL-3',
    
    'depends': ['account','base','account_reports'],
    
    'data': [
        'views/partner_ledger.xml',
        'views/partner_ledger_menu.xml',
        'security/ir.model.access.csv',
    ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
}

