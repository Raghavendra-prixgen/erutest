
{
    'name': 'Packing List',
    'version': '17.0.1.5',
    'summary': 'Packing List',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'description':"""Packing List""", 
    'App origin':'Projet Specific',
    'module_type':'official',
    'license': 'LGPL-3',
    'depends':['base','account','web','purchase','sale','stock','purchase_stock','sale_stock','account_accountant','l10n_in','odoo_e_14_b'],
    'data':[
        'security/ir.model.access.csv',
        'views/packing_list.xml',
        'views/cbm_calculation.xml',
        'wizard/get_package_lines.xml',

       
       
        ],
    'installable': True,
    'auto_install': False,
}

