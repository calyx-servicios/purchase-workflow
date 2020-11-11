from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    attachment_status = fields.Char(string='Attachments')
