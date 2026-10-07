# -*- coding: utf-8 -*-
{
    'name': "odooe31b",

    'summary': """
        Sale Base Odoo 17""",

    'description': """
        Included Functionalities - 
        1. Document Type 
        2. Sequence on Document Type
        3. Short Close For Sale Order
        4. Blanket sale order
        """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'module_type':'official',

    'category': 'Sale',
    'version': '17.0.0.5',
    'license': 'LGPL-3',
    'App origin':"Base",

    'depends': ['base','mail','product','sale_management','sale','crm','stock'],
    # 'inventory_base','analytic_base'

    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/sales_team_security.xml',
        'views/views.xml',
        'views/sale_restriction.xml',
        'views/blanket_order_view.xml',
        'views/customer_view.xml',
        'views/sale_short_close.xml',
        'wizard/create_sale_quotation_view.xml',
        'wizard/saleorder_short_close_wizard.xml',
        # 'wizard/sales_reject_views.xml',
        # 'views/sale_approval_view.xml',
    ],
}
