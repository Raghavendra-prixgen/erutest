# -*- coding: utf-8 -*-
{
    'name': "odooe27b",

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
    'version': '17.0.2.0',
    'license': 'LGPL-3',

    'depends': ['base','purchase','product','purchase_requisition_stock','sale_management','stock_landed_costs','account','analytic','stock','mail','purchase_stock','purchase_requisition'],

    'data': [
        "security/purchase_request.xml",
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence_data.xml',
        'data/down_payment_request_sequence.xml',
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",


        'views/purchase_order_view.xml',
        'views/stock_location_route_view.xml',
        'wizard/wiz_last_purchase_price.xml',
        'views/purchase_doc_type_views.xml',
        'views/purchase_uom.xml',
        'views/product_sourcing.xml',
        'views/active_view.xml',
        'wizard/choose_purchase_charges_views.xml',
        'views/purchase_tolerance_view.xml',
        'views/merge_po.xml',
        'views/incoterm.xml',
        'views/split_po.xml',


        'views/res_config_setting.xml',
        'views/advance_request_form.xml',
        'views/purchase_form_view.xml',

        "reports/report_purchase_request.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_request_line_view.xml",
        "views/purchase_request_report.xml",
        "views/product_template.xml",
        "views/purchase_order_request_view.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/request_type.xml",


        'wizard/purchase_short_close_wizard.xml',
        'views/purchase_short_close.xml',

        "views/purchase_orders_receipt_to_bill.xml"
        # 'views/master_delete_button.xml',


    ],
    'installable' : True,
	'auto_install': False,

}
# Product design - Domestic - Materials - TANF