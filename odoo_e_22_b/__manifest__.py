# -*- coding: utf-8 -*-
{
    'name': "odooe22b",

    'summary': """
        Material Requisition""",

    'description': """
        1. Creating a transfer for product from destination location to source location
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'module_type':'official',

    'category': 'Customization',
    'origin': 'base',
    'version': '17.0.1.3',
    'license': 'LGPL-3',

    'depends': ['base','stock','purchase','odoo_e_27_b'],

    'data': [
        'security/ir.model.access.csv',
        'views/material_request.xml',
    ],
}
