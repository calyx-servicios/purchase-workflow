from odoo import models, fields, _
from odoo.exceptions import UserError

class PurchaseMultiWarehouse(models.TransientModel):
    _name = 'purchase.multi_warehouse'
    _description = 'Wizard Multi Warehouse'

    order_id = fields.Many2one('purchase.order', string='Order ID')
    company_id = fields.Many2one('res.company', string='Company')
    picking_type_id = fields.Many2many('stock.picking.type', string='Deliver to')

    def charge_lines(self):
        try:
            if self.picking_type_id and self.order_id:
                multi_warehouse_obj = self.env['multi.warehouse']
                lines = multi_warehouse_obj.search([('order_id', '=', self.order_id.id)])
                if lines:
                    lines.unlink()
                order_lines = self.order_id.order_line
                for line in order_lines:
                    if line.product_id.is_fuel:
                        stock_picking = self.picking_type_id
                        for picking in stock_picking:
                            product_id =  picking.default_location_dest_id.product_id.id
                            if product_id == line.product_id.id:
                                multi_warehouse_obj.create({
                                'order_id': self.order_id.id,
                                'order_line_id': line.id,
                                'picking_type_id': picking.id,
                            })
                    else:
                        stock_picking = self.picking_type_id
                        for picking in stock_picking:
                            picking_id = picking.default_location_dest_id.product_id.is_fuel
                            if not picking_id:
                                multi_warehouse_obj.create({
                                    'order_id': self.order_id.id,
                                    'order_line_id': line.id,
                                    'picking_type_id': picking.id,
                                })
        except Exception as e:
            raise UserError(f'Error loading lines{e}')

    def multi_warehouse(self, window_title, order_id, company_id):
        wiz = self.create({
            'order_id': order_id,
            'company_id': company_id,
        })
        return wiz.open_wizard(window_title)

    def open_wizard(self, title):
        view = self.env.ref('multi_warehouse_per_order.wizard_multi_warehouse_form')
        return {
            'type': 'ir.actions.act_window',
            'name': title,
            'res_model': self._name,
            'target': 'new',
            'view_id': view.id,
            'view_mode': 'form',
            'res_id': self.id,
            'context': self.env.context,
        }