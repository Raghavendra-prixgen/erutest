# -*- coding: utf-8 -*-
{
    'name': "Odooe41",

    'description': """
        Included Functionalities - 

        Purchase Approval

    """,
    'summary': """ Odooe41 """,
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'module_type':'official',
    'App origin': "Project Specific",
    'category': 'Purchase',
    'version': '17.0.2.3',
    'license': 'LGPL-3',

    'depends': ['base', 'purchase', 'product', 'stock', 'purchase_stock','odoo_e_27_b'],


    'data': [
        "security/ir.model.access.csv",
        "security/security.xml",
        "wizard/purchase_reject_views.xml",
        "views/purchase_approval_view.xml",
        "views/product_template_view.xml",
        "views/record_rules.xml",
    ],
    'installable' : True,
	'auto_install': False,

}
