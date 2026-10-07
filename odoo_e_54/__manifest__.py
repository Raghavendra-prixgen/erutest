
{
    'name': 'Product Category',
    'version': '17.0.0.1',
    'summary': 'Product Category ',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'description':"""""", 
    'App origin':'Projet Specific',
    'module_type':'official',
    'license': 'LGPL-3',
    'depends':['base','account','web','purchase','sale','stock',],
    'data':[
        'security/ir.model.access.csv',
        'views/picking_type.xml',
        ],
    'installable': True,
    'auto_install': False,
}

