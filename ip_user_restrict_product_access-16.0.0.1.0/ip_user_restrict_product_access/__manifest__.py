# -*- coding: utf-8 -*-
{
    'name': 'User Restriction on Product Access',
    'summary': "User Restriction on Product Access by Allowing Selected Products or Category",
    'description': "User Restriction on Product Access by Allowing Selected Products or Category",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Others',
    'version': '16.0.0.1.0',
    'depends': ['product'],

    'data': [
        'security/users_product_security.xml',
        'views/res_users_view.xml',
    ],

    'license': "OPL-1",
    'price': 20,
    'currency': "EUR",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/banner.png'],
    'pre_init_hook': 'pre_init_check',
}
