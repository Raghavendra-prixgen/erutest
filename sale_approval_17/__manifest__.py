# -*- coding: utf-8 -*-
{
    'name': "Sale Approval Odoo 17 ",

    'summary': """
        Sale Approval Odoo 17""",

    'description': """
        Included Functionalities - 
        1. Sale Approval based on Document Type 
        
        """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'module_type':'official',

    'category': 'Sale',
    'version': '17.0.0.3',
    'license': 'LGPL-3',
    'App origin':"Base",

    'depends': ['base','mail','product','sale_management','sale','crm','stock','odoo_e_31_b'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_reject_views.xml',
        'views/sale_approval_view.xml',
    ],
}
