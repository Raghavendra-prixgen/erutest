{
    'name': 'odooe02',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',    
    
    'version': '17.0.1.0',
    
    'category': 'Purchase',

    'summary': 'This module is useful to show the purchase order lines with status of GRN and Invoice',

    'description': """This module is useful to show the purchase order lines with status of GRN and Invoice""" ,
    'module_type':'official',
    'App origin':'Base',
    'depends': ['purchase','stock','odoo_e_27_b','odoo_e_31_b'],
    
    'data': [
        'views/purchase_order_line.xml',
    ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
}

#  'analytic_base' remove from manifest because of testing purpus and comment related codes
