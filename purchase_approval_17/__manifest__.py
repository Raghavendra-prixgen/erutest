# -*- coding: utf-8 -*-
{
    'name': "Purchase Approval 17",

    'description': """
        Included Functionalities - 

        1. Document type
        2. Sequence for Document Type
        3. Product Souring
        4. Purchase Charges 
        5. Purchase gross amount
        6. Purchase tolerance
        7. Purchase Unit Of Measure
        8. Purchase Order Routing
        9. Purchase Request
        10. Purchase Advance Payment
        11. Purchase Short Close
        12. Purchase Receipt to Bill
        13. Merge Purchase Order
        14. Split Purchase Order

    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'module_type':'official',
    'App origin': "Base",
    'category': 'Purchase',
    'version': '17.0.0.3',
    'license': 'LGPL-3',

    'depends': ['base', 'purchase', 'product', 'stock', 'purchase_stock', 'purchase_base_17'],

    'data': [
        "security/ir.model.access.csv",
        "wizard/purchase_reject_views.xml",
        "views/purchase_approval_view.xml",
        "views/product_template_view.xml",
    ],
    'installable' : True,
	'auto_install': False,

}
