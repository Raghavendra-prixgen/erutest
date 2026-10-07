# -*- coding: utf-8 -*-
{
    'name': 'odoo_e_51',
    'version': '17.0.0.2',
    'category': 'Accounting',
    'App origin':'Base',
    'module_type':'official',
    'summary': 'Invoice Bank Upload Format',
    'description': """
		Invoice Bank Upload Format.
    				""",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',    

    'depends': ['base','account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_payment_reconciliation_wizard.xml',
    ],
    'installable': True,
    'auto_install': False
}
