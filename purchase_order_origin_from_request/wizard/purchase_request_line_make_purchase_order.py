# Copyright 2020 Calyx Servicios S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.multi
    def make_purchase_order(self):
        for item in self.item_ids:
            line = item.line_id
            line.origin = (
                item.request_id.name
                if not item.request_id.origin
                else item.request_id.origin
            )
        res = super(
            PurchaseRequestLineMakePurchaseOrder, self
        ).make_purchase_order()

        return res
