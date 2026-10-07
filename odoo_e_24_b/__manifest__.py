
# -*- coding: utf-8 -*-
{
    'name': "odooe24b",

    'summary': """
    """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "http://www.prixgen.com",
    'module_type':'official',
    'license': 'LGPL-3',
    'App origin':'Base',

    'category': 'Manufacturing',
    'version': '17.0.0.3',

    'depends': ['base','mrp','stock','mail','uom'],

    'data': [
        'data/sequence.xml',

        'security/ir.model.access.csv',
        'views/material_to_material_transfer.xml'
    ],
}
