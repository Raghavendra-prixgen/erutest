# -*- coding: utf-8 -*-
{
    'name': "Proforma Invoice Report",

    'summary': """
        """,

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",

    'version': '17.0.0.8',

    'depends': ['base','sale','web','custom_app_eruvaka'],

    'data': [
        'reports/proforma_invoice_temp.xml', 
        'reports/header_footer.xml', 
        'reports/proforma_invoice_temp_export.xml',
        'reports/header_footer_export.xml',
        
    ],
}
