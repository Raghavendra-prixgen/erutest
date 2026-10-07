
{
    'name': 'odooe33b',
    'version': '17.0.0.8',
    'category': 'Sale',
    'summary': 'Sale Register Report 17',
    'App origin':'Base',
    'description': """
		This module get the Sale summary between the given dates .
    				""",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',   
    'module_type':'official', 

    'depends': ['hr', 'sale','stock','product','account','base','l10n_in','odoo_e_11'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/Sale_report_wizard.xml',
        'views/sales_report.xml',
        'views/sales_report_view.xml',
    ],


    'installable': True,
    'auto_install': False
}

#odoo_e_11 is added becuase of free sample field