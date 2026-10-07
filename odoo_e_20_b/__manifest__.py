{
    'name': 'odooe20b',
    'version': '17.0.0.2',
    'category': 'Landed Costs',
    'origin': 'base',
    'module_type':'official',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base','stock','stock_landed_costs','mrp','product','mrp_landed_costs','stock_account','odoo_e_19_b'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/manufacturing_landed_cost.xml',
    ],

    
}


#manufacturing_base_17 is given because of using y_total_output_quantity field in stock move

