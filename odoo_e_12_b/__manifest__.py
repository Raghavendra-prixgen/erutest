# -*- coding: utf-8 -*-
{
    'name': "odooe12b",

    'summary': """
        This app enables a feature to map lot sequences on operartion types.
        """,

    'description': """
     This feature is developed to fulfill warehouse wise lot generation for raw materials at the time of GRN 
     and warehouse wise lot geneartion for FG at the time of manufacturing.
    """,
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'origin':'project specification',
    'category': 'Uncategorized',
    'version': '17.0.0.3',
    'license': 'LGPL-3',
    'depends': ['base','stock','mail','sale','purchase','mrp'],
    'data': [
        'views/mrp_production.xml',
        'views/stock_move.xml',
        'views/stock_picking_type.xml',
        'views/stock_prodcution_lot.xml',
    ],
}
