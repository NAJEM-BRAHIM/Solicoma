# -*- coding: utf-8 -*-
{
    "name": "SIS Caja Virtual",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "summary": "Control de Cajas Virtuales en Pedidos, Albaranes y Facturas",
    "description": """
        Gestión de cajas virtuales en líneas de pedido de venta,
        movimientos de stock, cuantos e inventario.
    """,
    "author": "Sahara Info Service",
    "license": "LGPL-3",
    "depends": ["sale", "account", "stock", "sale_stock"],
    "data": [
        "views/product_views.xml",
        "views/sale_views.xml",
        "views/invoice_views.xml",
        "views/stock_views.xml",
        "views/sale_report.xml",
        "views/stock_report.xml",
        "views/report_invoice.xml",
    ],
    "application": False,
    "installable": True,
}
