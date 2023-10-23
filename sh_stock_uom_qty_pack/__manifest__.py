# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Inventory Quantity Pack | Incoming Order Quantity Pack | Outgoing Order Quantity Pack | Internal Transfer Quantity Pack",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "16.0.1",

    "category": "Warehouse",

    "license": "OPL-1",

    "summary": "Product Quantity Pack,Bundle Product Quantity,Stock Bundle Product, Manage Product Package, Product Quantity In Bags,Inventory Products Pack, Combo Products Quantity,Stock Product Pack,Bunch Product Quantity, Product Qty Pack Odoo",

    "description": """This module will allow you to assign the product quantity in bags and then when you put bags quantity it will default count total quantity based on bags quantity in incoming order/outgoing order/internal transfer. If you are selling some products in bulk quantity in the package, pack, bags. For example, a 25kg Sugar bag, so our module useful to add that bag quantity in line and it will auto calculate the final quantity. i,e 5 bags of 25kg sugar bag then auto calculate 125kg in the quantity field. You can hide/show bag size in incoming order/outgoing order/internal transfer as well hide/show bag size in the reports.""",

    "depends": [
        "stock","sh_base_uom_qty_pack",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/stock_picking_views.xml",
        "report/stock_picking_operation_templates.xml",
        "report/stock_picking_report_delivery_templates.xml",
    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 15,
    "currency": "EUR"
}
