
{
    'name': "Sale Document Notification",
    'version': "17.0.0.1",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'summary': 'Sale Document Notification',
    'category': "",
    'website': 'https://www.prixgen.com',
    'depends': ['base','sale', 'sale_base_17'],  
    'data': [
        'data/email_template_sale.xml',
        'data/mail_schedule_cron_sale.xml',
        'security/ir.model.access.csv',
        'views/sale_order.xml',        
        ],
    'demo': [],
    'installable': True,
    'application': False,

}
