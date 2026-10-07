{
    'name': "odooe32",
    'version': "17.0.0.6",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'summary': 'Sale Document Notification',
    'category': "",
    'origin': 'Project Specific',
    'license': 'LGPL-3',
    'module_type':'official',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'depends': ['base','sale', 'odoo_e_31_b'],  
    'data': [
        'data/email_template_sale.xml',
        'data/mail_schedule_cron_sale.xml',
        'security/ir.model.access.csv',
        'views/sale_order.xml',  
        'views/customer_sale_documentation.xml',
    ],
    
    'demo': [],
    'installable': True,
    'application': False,

}
