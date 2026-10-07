# -*- coding: utf-8 -*-
{
    'name': "Odooe52",

    'summary': "Odooe52",

    'description': """
       Sampling added to Quality
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'App origin':"Project Specific",
    'version': '17.0.0.1',
    'module_type':'official',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','product','quality','quality_control','odoo_e_30_b',],

    # always loaded
    'data': [
        'data/item_data.xml',
        'security/ir.model.access.csv',
        'views/sample_view.xml',
        'views/quality_point_view.xml',
        'views/sample_observation.xml',
        'views/visual_type.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

