{
    'name': 'odooe06b',
    'version': '17.0.0.2',
    'summary': 'Analytic Customization',
    'description': """
    Analytic Accounts auto flows covered-
        - SO            ->  DC
        - SO            ->  INV
        - PO            ->  GRN
        - PO            ->  BILL
        - PAY           ->  ACC
        - SO            ->  MO
        - PO            ->  MO
        - MO            ->  PO
        - MO            ->  CHILD MO
        - MO            ->  RAW-PROC
        - TNF(SO/PO/MO) ->  VAL
        - INV-ADJ       ->  VAL
        - EXP           ->  JV
        - EXP           ->  PAY
        - AA-DIST       ->  SO
        - AA-DIST       ->  PO
        - AA-DIST       ->  MO
        - AA-DIST       ->  TNF
    """,
    'module_type':'official',
    'category': 'Customization',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'depends': ['base','web','sale','stock','account','sale_mrp','analytic','purchase','sale_stock','hr_expense','stock_account','purchase_stock','account_asset'],
    'data': [
        'views/analytic.xml',
        'views/stock.xml',
        'views/payment.xml',
        'views/mrp.xml',
        ],

    'license': 'LGPL-3',
    'installable' : True,
	'auto_install': False,

}
