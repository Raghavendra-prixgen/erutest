# -*- coding: utf-8 -*-
{
    'name': 'Purchase Short Close - Service Products',

    'version': '17.0.0.2',

    'summary': 'Use Billed Qty as Received Qty for Service products in Purchase Short Close',

    'description': """
        This App enhances the Purchase Short Close Wizard for Service products.

        Problem it solves
        ------------------
        Service products do not generate GRNs/stock moves, so the standard
        qty_received remains 0.00 even when the service has been fully billed.

        What this app does
        -------------------
        1. Service products use Billed Qty as Received Qty.
        2. Storable/Consumable products continue using GRN Qty.
        3. Each Purchase Order line is evaluated independently.
        4. Mixed Service and Storable/Consumable Purchase Orders are supported.
    """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',

    'App origin': 'Projet Specific',
    'module_type': 'official',

    'category': 'Purchase',
    'license': 'LGPL-3',

    'depends': [
        'purchase',
        'odoo_e_27_b',
        'odoo_e_02',
    ],

    'data': [
        'views/purchase_short_close_wizard_views.xml',
    ],

    'installable': True,
    'auto_install': False,
}