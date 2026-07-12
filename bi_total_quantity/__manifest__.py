{
    'name': 'Total Number of Items/Quantity',
    'summary': 'Products/Items Total Number of Quantities',
    'version': '19.0.0.0',
    'category': 'Sales',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'license': 'OPL-1',
    'depends': ['sale', 'purchase', 'stock'],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
