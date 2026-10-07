# -*- coding: utf-8 -*-
{
    'name': "odooe23b",

    'summary': """
        Material Requisition Addons Mrp""",

    'description': """
        1. Generate Material request for manufacturing orders 
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'module_type':'official',

    'category': 'Customization',
    'origin': 'base',
    'version': '17.0.0.1',
    'license': 'LGPL-3',

    'depends': ['base','stock','purchase','mrp','odoo_e_22_b'],

    'data': [
        'views/mrp_material_request.xml',
    ],
}
