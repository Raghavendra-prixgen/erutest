# -*- coding: utf-8 -*-
{
    'name': "odooe38b",

    'summary': """""",
    'sequence': 4,
    'version': '17.0.0.3',

    'description': """
        1.By installing this module, user can see Mandatory Field with red asterisk symbol,
            along with table header freeze(sticky) inside the form view.
        2. User can see row-serial number automatically getting generated 
            for all/ entire Tree View structure. 
        3. Pviot Table Header is freezed.    
        
    """,
    'module_type':'official',

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'App origin':'Base',
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    'depends': ["base","web",'account','hr_expense','purchase'],
    'data': [],

    'assets': {
        'web.assets_backend': [
            'odoo_e_38_b/static/src/css/form_asset.css',
            'odoo_e_38_b/static/src/xml/pivot.xml',
            'odoo_e_38_b/static/src/scss/mandatory_field_highlight.scss',
            # 'odoo_e_38_b/static/src/xml/rowno.xml',
            'odoo_e_38_b/static/src/scss/list_view.scss',
            # 'odoo_e_38_b/static/src/xml/list_render.xml',
            'odoo_e_38_b/static/src/scss/acounts.scss',
            # 'odoo_e_38_b/static/src/xml/list_render_exp.xml',
            'odoo_e_38_b/static/src/scss/expense.scss',
            # 'odoo_e_38_b/static/src/xml/list_render_purchase.xml',
            'odoo_e_38_b/static/src/scss/purchase.scss',
            'odoo_e_38_b/static/src/js/account_accountant.js',
        ],
    },
}
