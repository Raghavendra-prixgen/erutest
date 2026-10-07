# -*- coding: utf-8 -*-
{
    'name': "Custom Login - Odoo.com Only",

    'summary': """ Hide email/password login, show only Log in with Odoo.com """,
    'origin': "Project Specific",

    'description': """
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'license': 'LGPL-3',
    'website': "https://www.prixgen.com",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",

    'version': '17.0.0.1',

    'depends': ['web', 'auth_oauth'],

    'data': [
        'views/login_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_login_odoo/static/src/css/login_hide.css',
        ],
    },
    'installable': True,
    'auto_install': False,
}
