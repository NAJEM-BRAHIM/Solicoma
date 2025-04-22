# -*- coding: utf-8 -*-

# Part of Softhealer Technologies.

{
    'name': 'Cancel Sale orders | Cancel SO',
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    'support': 'support@softhealer.com',
    'category': 'Sales',
    'license': 'OPL-1',
    'summary': 'Cancel Sale Orders, Cancel Sale Order, Cancel SO,Sale Order Cancel, Sale Orders Cancel, Cancel Quotation, Cancel Quotate,Sale Cancel, Cancel Quotes,Delete Sale Order,Delete SO,Sale Order Delete, Remove Sale, Remove Quote Odoo',
    'description': """This module helps to cancel created sale orders. You can also cancel multiple sale orders from the tree view. You can cancel the sale order in 3 ways,

1) Cancel Only: When you cancel a sale order then the sale order is cancelled and the state is changed to "cancelled".
2) Cancel and Reset to Draft: When you cancel sale order, first sale order is cancelled and then reset to the draft state.
3) Cancel and Delete: When you cancel a sale order then first sale order is cancelled and then sale order will be deleted.

We provide 2 options in the cancel sales orders,

1) Cancel Delivery Order: When you want to cancel sale orders and delivery orders then you can choose this option.
2) Cancel Invoice and Payment: When you want to cancel sale orders and invoice then you can choose this option.

If you want to cancel sale orders, delivery orders & invoice then you can choose both options "Cancel Delivery Order" & "Cancel Invoice and Payment".""",
    'version': '16.0.1',
    'depends': ['sale_management'],
    'application': True,
    'data': ['security/sale_security.xml', 'data/server_action_data.xml', 'views/sale_config_settings_views.xml', 'views/sale_order_views.xml'
             ],
    'images': ['static/description/background.png'],
    'auto_install': False,
    'installable': True,
    'price': 20,
    'currency': 'EUR',
}
