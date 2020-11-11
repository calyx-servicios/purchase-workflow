##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo import exceptions
from dateutil.relativedelta import relativedelta
import re
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	supplier_id = fields.Many2one('res.partner', string='Supplier')

class SaleOrder(models.Model):
	_inherit = "sale.order"

	purchase_ids = fields.Many2many('purchase.order', relation='sale_purchase_rel', column1='sale_id',column2='purchase_id', string="Purchases")

	@api.multi
	def _action_confirm(self):
		ret = super(SaleOrder, self)._action_confirm()
		order_ids = []
		for line in self.order_line:
			if not line.supplier_id:
				continue
			vals_line =  { 'product_id': line.product_id.id,
							'name': line.name,
							'date_planned': self.confirmation_date,
							'price_unit' : line.purchase_price,
							'product_qty' : line.product_uom_qty,
        					'product_uom' : line.product_id.uom_po_id.id or line.product_id.uom_id.id, 
        					'account_analytic_id': self.analytic_account_id.id,
        					}
			vals = {
				'partner_id': line.supplier_id.id,
				'user_id': self.user_id.id,
				'currency_id': self.pricelist_id.currency_id.id,
				'date_order': self.confirmation_date,
				'date_planned': self.confirmation_date,
				'order_line': [(0, 0, vals_line)],
			}
			process = 0
			for order in order_ids:
				if order.partner_id == line.supplier_id:
					order.write({'order_line': [(0, 0, vals_line)]})
					process = 1
			if process == 0:
				order_id = order_ids.append(self.env['purchase.order'].create(vals))

		for order in order_ids:
			self.write({'purchase_ids': [(4, order.id)]})
		return ret

	@api.multi
	def action_cancel(self):
		for so in self:
			for po in so.purchase_ids:
				if po.state not in ['draft', 'cancel']:
					raise exceptions.Warning('Una o mas ordendes de compra relacionadas a este presupuesto estan confirmadas. Cancele dischas ordenes de  compra y vuelva a intentarlo')
				else:
					po.button_cancel()
					po.unlink()
		ret = super(SaleOrder, self).action_cancel()