
{
    'name': 'odooe53',
    'version': '17.0.0.2',
    'category': 'COGS',
    'summary': 'COGS Register Report 17',
    'App origin':'Project Specification',
    'description': """
		This module get the COGS summary between the given dates .
    				""",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',   
    'module_type':'official', 

    'depends': ['hr', 'sale','stock','product','account','base','l10n_in','odoo_e_11'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cogs_report_wizard.xml',
        'views/cogs_report_view.xml',
    ],


    'installable': True,
    'auto_install': False
}

