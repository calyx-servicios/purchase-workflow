{
    "name": "Multi Warehouse Per Order",
    "summary": """
        This module allows from an order to choose multiple warehouses.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["Zamora, Javier"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Purchase",
    "version": "13.0.2.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": [
        'purchase_stock',
        'stock',
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizards/purchase_multi_warehouse.xml',
        'views/purchase_order.xml',
    ],
}
