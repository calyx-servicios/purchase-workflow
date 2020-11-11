import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    # ----------------------------------------------------------
    # Create and Delete
    # ----------------------------------------------------------

    @api.multi
    def create(self, vals):
        res = super(IrAttachment, self).create(vals)
        if vals.get('res_model', False) == 'purchase.order':
            po_attchs = self.env['ir.attachment'].search(
                [('res_model', '=', 'purchase.order'),
                 ('res_id', '=', vals.get('res_id', False))]
            )

            rec = self.env['purchase.order'].browse(vals.get('res_id', False))

            if len(po_attchs) == 1:
                rec.write({'attachment_status': 'Has attachment'})
            if len(po_attchs) > 1:
                rec.write({'attachment_status': 'Has %d attachments' % len(po_attchs)})

        _logger.info("Updated attachment_status field to 'Has attachments' of Purchase Order id %s"
                     % vals.get('res_id'))
        return res

    @api.multi
    def unlink(self):
        """
        We check if the current attachment model is 'purchase.order', if it is,
        then write False on attachment_status in case we have only 1 attachment
        that will be 0 after unlink() method is called.

        :return: attachment delete.
        """
        for record in self:
            attachment = self.env['ir.attachment'].browse(record.id)
            if attachment.res_model == 'purchase.order':
                po_attchs = self.env['ir.attachment'].search(
                    [('res_model', '=', 'purchase.order'),
                     ('res_id', '=', attachment.res_id)]
                )

                po = self.env['purchase.order'].search(
                    [('id', '=', attachment.res_id)]
                )

                if len(po_attchs.ids) == 1:
                    po.write({'attachment_status': False})
                elif len(po_attchs.ids) > 1:
                    po.write({'attachment_status': 'Has %d attachments' % (len(po_attchs) - 1)})

                    _logger.info("Updated attachment_status field to False of Purchase Order %s" % po.display_name)
            res = super(IrAttachment, self).unlink()
            return res
