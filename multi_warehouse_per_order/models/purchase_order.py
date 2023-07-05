from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    multi_warehouse_ok = fields.Boolean('Multi-Warehouse', default=False)
    multi_warehouse_ids = fields.One2many('multi.warehouse', 'order_id')
    total_quantity = fields.Float(compute='_compute_total_quantity', string='Total on Product Lines') 
    total_current_quantity_available = fields.Float(compute='_compute_total_current_quantity_available', string='Total Current Quantity Available')
    current_total = fields.Float(compute='_compute_current_total', string='Current Total on Product Lines')

    @api.depends('order_line.product_qty')
    def _compute_total_quantity(self):
        self.total_quantity = sum(self.order_line.mapped('product_qty'))
    
    @api.depends('current_total', 'total_quantity')
    def _compute_total_current_quantity_available(self):
        self.total_current_quantity_available = self.total_quantity - self.current_total

    @api.depends('multi_warehouse_ids.new_quantity')
    def _compute_current_total(self):
        self.current_total = sum(self.multi_warehouse_ids.mapped('new_quantity'))

    @api.constrains('multi_warehouse_ids')
    def _constrains_fieldname(self):
        for rec in self:
            for warehouse in rec.multi_warehouse_ids:
                if warehouse.quantity_available < 0:
                    raise UserError(_('Cannot exceed Total Required'))

    def charge_lines(self):
        order_id = self.id
        company_id = self.company_id.id
        return self.env['purchase.multi_warehouse'].multi_warehouse(_('Choose Warehouse'), order_id, company_id)

    def _create_picking(self):
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if order.multi_warehouse_ok:
                if sum(order.multi_warehouse_ids.mapped('quantity_available')) != 0:
                    raise UserError(_('The quantities available in the warehouse options must be at 0'))
                if any(product.type in ['product', 'consu'] for product in order.multi_warehouse_ids.product_id):
                    order = order.with_company(order.company_id)
                    pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    if not pickings:
                        picking = order._create_multi_picking(self)
                    else:
                        picking = pickings[0]
                    return picking
            else:
                return super(PurchaseOrder, self)._create_picking()

    def button_confirm(self):
        for rec in self:
            if rec.multi_warehouse_ok:
                warehouses = rec.multi_warehouse_ids.filtered(lambda x: x.quantity_available != 0)
                if warehouses:
                    message = _('The following warehouses have quantities available: \n {}.'
                                '\nPlease set on this lines the available quantity to 0.').format(
                        ',\n '.join(warehouses.mapped('name')))
                    raise UserError(message)
                elif not rec.multi_warehouse_ids:
                    raise UserError(_('Please complete the warehouse options before confirming'))
        return super(PurchaseOrder, self).button_confirm()
                

    def _create_multi_picking(self, order):
        picking_obj = self.env['stock.picking']
        for warehouse in order.multi_warehouse_ids.mapped('picking_type_id'):
            res = self._prepare_multi_picking(order, warehouse)
            picking = picking_obj.with_user(SUPERUSER_ID).create(res)
            warehouse_lines = order.multi_warehouse_ids.filtered(lambda m: m.picking_type_id.id == warehouse.id)
            for lines in warehouse_lines:
                moves_values = order._prepare_multi_stock_move_vals(picking, lines)
                moves = self.env['stock.move'].create(moves_values)
                moves = moves._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

    def _prepare_multi_stock_move_vals(self, picking, line):
        date_planned = line.order_line_id.date_planned or line.order_id.date_planned

        return {
            'name': (line.order_line_id.product_id.display_name or '')[:2000],
            'product_id': line.order_line_id.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned,
            'location_id': line.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (line.order_line_id.orderpoint_id and not (line.order_line_id.move_ids | line.order_line_id.move_dest_ids)) and line.order_line_id.orderpoint_id.location_id.id or line.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': line.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in line.order_line_id.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': line.order_line_id.id,
            'company_id': line.order_id.company_id.id,
            'price_unit': line.order_line_id.price_unit,
            'picking_type_id': line.picking_type_id.id,
            'group_id': line.order_id.group_id.id,
            'origin': line.order_id.name,
            'description_picking': line.order_line_id.product_id.description_pickingin,
            'propagate_cancel': line.order_line_id.propagate_cancel,
            'warehouse_id': line.picking_type_id.warehouse_id.id,
            'product_uom_qty': line.new_quantity,
            'product_uom': line.order_line_id.product_uom.id,
            'product_packaging_id': line.order_line_id.product_packaging_id.id,
            'sequence': line.order_line_id.sequence,
        }

    def _prepare_multi_picking(self, order, warehouse):
        if not order.group_id:
            order.group_id = order.group_id.create({
                'name': order.name,
                'partner_id': order.partner_id.id
            })

        if not order.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", order.partner_id.name))

        return {
            'picking_type_id': warehouse.id,
            'partner_id': order.partner_id.id,
            'user_id': False,
            'date': order.date_order,
            'origin': order.name,
            'location_dest_id': warehouse.default_location_dest_id.id,
            'location_id': order.partner_id.property_stock_supplier.id,
            'company_id': order.company_id.id,
        }