# -*- coding: utf-8 -*-
{
    'name': "xg_qc_custom",

    'summary': "Sampling added to Quality",

    'description': """
       Sampling added to Quality
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'App origin':"Project Specific",
    'version': '17.0.0.2',
    'module_type':'official',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','product','quality','quality_control','quality_control_base',],

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

