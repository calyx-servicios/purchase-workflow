# Copyright 2020 Calyx Servicios S.A
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from odoo import models, api


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    @api.model
    def create(self, vals):
        pr_name = vals.get("name")
        vals["origin"] = pr_name if pr_name else False
        return super(PurchaseRequest, self).create(vals)
