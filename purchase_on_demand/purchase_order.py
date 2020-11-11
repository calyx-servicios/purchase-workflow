##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re
import logging
_logger = logging.getLogger(__name__)


class PruchaseOrder(models.Model):
	_inherit = "purchase.order"

	sale_ids = fields.Many2many('sale.order', relation='sale_purchase_rel', column1='purchase_id',column2='sale_id', string="Sales")
	