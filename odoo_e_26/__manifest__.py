# -*- coding: utf-8 -*-
{
    'name': "odooe26",

    'description': """
        Included Functionalities - 

        Purchase Approval

    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'module_type':'official',
    'App origin': "Base",
    'category': 'Purchase',
    'version': '17.0.1.0',
    'license': 'LGPL-3',

    'depends': ['base', 'purchase', 'product', 'stock', 'purchase_stock', 'odoo_e_27_b'],


    'data': [
        "security/ir.model.access.csv",
        "wizard/purchase_reject_views.xml",
        "views/purchase_approval_view.xml",
        "views/product_template_view.xml",
    ],
    'installable' : True,
	'auto_install': False,

}
