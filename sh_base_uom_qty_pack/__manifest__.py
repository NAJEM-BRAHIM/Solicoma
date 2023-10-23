# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Base Product Quantity Pack",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "16.0.1",
    "license": "OPL-1",
    "category": "Extra Tools",
    "summary": "Sale Order Quantity Pack,Purchase Order Quantity Pack,Bundle Product Quantity, Manage Product Package, Product Quantity In Bags, Combo Products Quantity,Bunch Product Quantity, Product Qty Pack,Invoice Quantity Pack,Inventory Quantity Pack Odoo",
    "description": """"Base Product Quantity Pack" module is a base module for Quantity Pack modules.""",
    "depends": [
        "product","stock",
    ],
    "data": [
        "views/product_product_views.xml",
        "views/product_template_views.xml",
    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 1,
    "currency": "EUR"
}
