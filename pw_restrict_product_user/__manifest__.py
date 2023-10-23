# -*- coding: utf-8 -*-

{
    'name': 'Product Restriction on Users',
    'category': 'Extra Tools',
    'summary': 'This module will helps you to allow product to user or only access products related to allowed category | Allow access of products/category to user | User Restriction on Product Access',
    'version': '1.0',
    'author': 'Preway IT Solutions',
    'description': """Restrict Product to user : 
- Display/Visible selected products to user.
- Display/Visible selected products related to category.

- Show selected product to user.
- Show selected product to related category
    """,
    'depends': ['product'],
    'data': [
        'security/product_security.xml',
        'views/res_users_view.xml',
    ],
    'price': 15.0,
    'currency': "EUR",
    'application': True,
    'installable': True,
    "license": "LGPL-3",
    'live_test_url': 'https://youtu.be/qw_BVi31KGs',
    'images': ["static/description/Banner.png"],
}
