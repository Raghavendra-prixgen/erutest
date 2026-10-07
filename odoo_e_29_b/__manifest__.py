# -*- coding: utf-8 -*-
{
    'name': 'odooe29b',
    'version': '17.0.0.8',
    'category': 'Purchase',
    'summary': 'Purchase Register Report 17',
    'App origin':'Base',
    'description': """
		This module get the Purchase summary between the given dates .
    				""",
    'module_type':'official',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',    

    'depends': ['hr', 'purchase','stock','product','account','base','crm'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_report_wizard.xml',
        'views/purchase_report.xml',
        'views/purchase_report_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
