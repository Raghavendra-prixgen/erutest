{
    'name': "odooe03",

    'summary': """ odooe03 """,

    'description':"""
        This module is useful to show the sale order lines with status of Delivery and Invoice""",
    
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com', 
    'module_type':'official',   
    
    'category': 'Sales',
    'version': '17.0.0.4',
    'App origin':'Base',

    'license': 'LGPL-3',
    
    'depends': ['sale','sale_stock','odoo_e_17_b','odoo_e_31_b'],
    
    'data': [
        'views/sale_order_line.xml',
    ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
}

#  'analytic_base' remove from dependency because of testing purpose
