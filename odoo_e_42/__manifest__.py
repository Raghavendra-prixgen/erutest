# -*- coding: utf-8 -*-
{
    'name': "Odooe42 ",

    'summary': """
        Odooe42""",

    'description': """
        Included Functionalities - 
        1. Sale Approval
        
        """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'module_type':'official',

    'category': 'Sale',
    'version': '17.0.1.2',
    'license': 'LGPL-3',
    'App origin':"Base",

    'depends': ['base','mail','product','sale_management','sale','crm','stock','odoo_e_31_b'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/sales_reject_views.xml',
        'views/sale_approval_view.xml',
        'views/record_rules.xml',

    ],
}
