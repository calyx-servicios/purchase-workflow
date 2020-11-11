# -*- encoding: utf-8 -*-

{
    'name': 'Purchase on demand',
    'version': '0.1',
    'category': 'Sales and Purchases',
    'license': 'AGPL-3',
    'summary': 'Add the reverse link from invoices to sale orders',
    'description': """
Sale Purchase Link
=========================

    """,
    'author': 'Calyx',
    'website': 'http://www.calyxservicios.com.ar',
    'depends': ['purchase', 'sale', 'sale_margin'],
    'data': ['sale_order_view.xml',
            'purchase_order_view.xml'], 
    'installable': True,
    'active': False,
}
