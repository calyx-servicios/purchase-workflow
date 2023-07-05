from odoo import models, fields, api, _


class MultiWarehouse(models.Model):
    _name = 'multi.warehouse'
    _description = 'Multi Warehouse'


    order_id = fields.Many2one('purchase.order', string='Order ID')
    order_line_id = fields.Many2one('purchase.order.line', string='Line ID')
    product_id = fields.Many2one('product.product', related='order_line_id.product_id', string='Product')
    quantity = fields.Float(related='order_line_id.product_qty', string='Quantity')
    new_quantity = fields.Float(string='Set Quantity')
    name = fields.Text(related='order_line_id.name', string='Description')
    company_id = fields.Many2one('res.company', related='order_id.company_id', string="Company")
    picking_type_id = fields.Many2one('stock.picking.type', string='Deliver to')
    quantity_available = fields.Float(compute='_compute_quantity_available', string='Quantity Available')
    status = fields.Selection([
        ('complete', 'Complete'),
        ('incomplete', 'Incomplete')], string='Status', default='incomplete', compute='_compute_status')

    @api.depends('new_quantity', 'quantity')
    def _compute_quantity_available(self):
        for rec in self:
            warehouses = rec.search([('order_id', '=', rec.order_id.id), ('order_line_id', '=', rec.order_line_id.id)])
            new_value = rec.quantity - sum(warehouses.mapped('new_quantity'))
            if rec.quantity != new_value:
                rec.quantity_available = new_value
            else:
                rec.quantity_available = rec.quantity - rec.new_quantity


    @api.depends('quantity_available')
    def _compute_status(self):
        for rec in self:
            if rec.quantity_available == 0:
                rec.status = 'complete'
            else:
                rec.status = 'incomplete'
