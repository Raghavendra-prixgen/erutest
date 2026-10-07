# -*- coding : utf-8 -*-

{
    'name' : 'odooe01b',
    'summary' : '',
    'description' : '',
    'module_type':'official',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com', 
    'version' : '17.0.0.5',
    'category': 'Purchase',
    'depends': ['base','stock'],
    'data': [
        'data/parent_company_data.xml',
        'security/ir.model.access.csv',
        'views/view.xml',
    ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
}

