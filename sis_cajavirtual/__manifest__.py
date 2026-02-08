# -*- coding: utf-8 -*-
{
    'name': 'Management of Virtual Boxes',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Management of Virtual Boxes',
    'description': """Management of Virtual Boxes""",
    'author': 'Sahara Info Service',
    'maintainer': 'Sahara Info Service',
    'depends': ['sale', 'account', 'stock', 'sale_stock'],
    'data': [
        'views/sale_views.xml',
        'views/invoice_views.xml',
        'views/stock_views.xml',
        'views/sale_report.xml',
        'views/stock_report.xml',
        'views/product_views.xml',
    ],
    'application': False,
    'installable': True,    
    'license': 'LGPL-3',    
}
