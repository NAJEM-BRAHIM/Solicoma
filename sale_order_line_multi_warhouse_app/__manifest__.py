# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Lines Multi Warehouse',
    "author": "Edge Technologies",
    'version': '16.0.1.0',
    'live_test_url': "https://youtu.be/O1hgViRnWEs",
    "images":['static/description/main_screenshot.png'],
    'summary':'Sale order line by warehouse sale order multiple warehouse sale order multiple warehouse sale multi warehouse sales multi warehouse by sale order line warehouse by sale line wise warehouse sale order line wise warehouse on sale order line warehouse select',
    'description': """
        
    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/sale_multi_warehouse.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 18,
    'currency': "EUR",
    'category': 'Sales',
}