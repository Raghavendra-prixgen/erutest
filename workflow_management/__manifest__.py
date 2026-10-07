# -*- coding: utf-8 -*-
{
    'name': 'Workflow Management-With Model wise Approval',
    'version': '17.0.0.8',
    'summary': 'Workflow Management',
    'license':'AGPL-3',
    'description': """
     Workflow Management.
""",
    'module_type':'official',

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'App origin':'Base',
    'depends': [
        'base_automation',
        'base_import_module',
        'mail',
        'web',
        'web_enterprise',
        'web_editor',
        'web_map',
        'web_gantt',
        'web_cohort',
        'sms',
        'mrp'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/workflow_management.xml',
        'data/mail_templates.xml',
        'data/mail_activity_type_data.xml',
    
             ],

    #     'assets': {
    #     'web.assets_backend': [
    #         # 'workflow_management/static/src/approval/approval_hook.js',
    #         'workflow_management/static/src/approval/approval_infos.js',            
    #         'workflow_management/static/src/approval/form_controller.js',       
    #         'workflow_management/static/src/approval/global_approval.js',
    #         'workflow_management/static/src/approval/view_button_approval.js',

    #         'workflow_management/static/src/approval/**/*',
    #         'workflow_management/static/src/**/*.xml',
    #     ],
        
       

    # }
   
}


