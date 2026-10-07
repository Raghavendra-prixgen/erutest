# -*- coding: utf-8 -*-
{
    'name': "Packing List Report",

    'summary': """ Packing List Report """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",

    'version': '17.0.0.3',

    'depends': ['base', 'sale', 'stock', 'odoo_e_11','odoo_e_14_b'],

    'data': [
        'reports/packing_list_report_temp.xml', 
        'reports/header_footer.xml',         
    ],
}
