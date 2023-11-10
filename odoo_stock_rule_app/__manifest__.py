{
    'name': 'Stock Location Restrictions and Access Controls App',
    'author': 'Edge Technologies',
    'version': '16.0.1.0',
    'live_test_url':'https://www.youtube.com/watch?v=h10s9IjesMU',
    "license": "OPL-1",
    "images":['static/description/main_screenshot.png'],
    'category': 'Warehouse',
    'price': 15,
    'currency': "EUR",
    'summary': 'Stock access control warehouse access control stock access rules warehouse access rules stock location restrictions warehouse location restrictions inventory location restrictions inventory access control inventory access rules on stock location restrict.',
    'description': "Stock location restrictions app",
    'depends': [
        'stock'
    ],
    'data': [
    	'security/security.xml',
    	'views/inherited_stock_location_view.xml',
    	'views/inherited_res_users_view.xml',
    ],
    'qweb' : [],
    'demo': [],
    'css': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
