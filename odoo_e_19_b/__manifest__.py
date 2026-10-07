# -*- coding: utf-8 -*-
{
    'name': "odooe19b",

    'summary': """
        Manufacturing Base Odoo 17""",

    'description': """
        Included Functionalities -
        1. Manufacturing product related stock move report
        2. Added Product category in Production Analysis 
        3. Item group in mrp.production pivot view
        4. Validation on excess of unbuild MO Qty (mrp.unbuild) 
        5. Reference of sale order & customer to workorder 
        6. Reference of sale order to purchase order & pickings 
        7. Workorder output Qty updatation & Validation on output Qty 
        8. Validation on operations(operation not started)
        9. Waring on consumption
        10.Work order restriction based on stock availablity 
        11.Manufacturing components SL no
        12.Logs for MO;unbuild;Scrap;BOM
        13.Restriction on delete button in masters
        14.Restriction on create & Edit in Manufacturing module
    """,
    'module_type':'official',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'App origin':'Base',

    'category': 'Manufacturing',
    'version': '17.0.0.3',
    'App origin':"Base",

    'license': 'LGPL-3',

    'depends': ['mrp','base','sale','mrp_account_enterprise','mrp_subcontracting','purchase','product','purchase_stock'],
# 'inventory_base',
    'data': [
        'security/ir.model.access.csv',
        'security/mo_user_validation.xml',
        # 'views/item_group.xml',
        'views/workcenter_category.xml',
        'views/saleorder_number.xml',
        # 'views/restriction.xml',
        'views/master_delete_button.xml',
        'views/bom_report.xml',
        'views/purchase_order_view.xml'
    ],
}
