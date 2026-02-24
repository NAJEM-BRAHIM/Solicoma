# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': "Receipt Transfer with Cost Price",
    'version': "19.0.0.1",
    'category': "Warehouse",
    'summary': "Receipt Cost Price in receipt purchase receipt costing receipt stock valuation costing on receipt with costing receipt valuation Inventory valuation cost with receipt cost price for valuation costing with receipt picking costing picking with cost price",
    'description': """

             Receipt Transfer with Cost Price in odoo,
             Set Cost Price in Receipt in odoo,
             Custom Cost Price in odoo,
             Inventory Valuation with Newly Custom Cost Price in odoo,
             Inventory Valuation in odoo,
             Set Product Cost Price on Receipt Transfer in odoo,

    """,
    'author': "BROWSEINFO",
    "price": 45,
    "currency": 'EUR',
    "website": "https://www.browseinfo.com/demo-request?app=bi_receipt_transfer_with_cost&version=19&edition=Community",
    'depends': ['base', 'stock_account', 'purchase_stock'],
    'data': [
        'views/stock_picking_inherit_view.xml'
    ],
    "license": 'OPL-1',
    'installable': True,
    'auto_install': False,
    "live_test_url": "https://www.browseinfo.com/demo-request?app=bi_receipt_transfer_with_cost&version=19&edition=Community",
    "images": ['static/description/Banner.gif'],
}
