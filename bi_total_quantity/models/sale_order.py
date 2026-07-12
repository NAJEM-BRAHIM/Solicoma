# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
# Fix Sahara Info Services: iteración sobre self para evitar
# "ValueError: Expected singleton" en recomputes por lotes.

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_quantity = fields.Float(string='No. Ordered Quantity', compute='_compute_total_order_quantity', default=0)
    deliver_quantity = fields.Float(string='No. Delivered Quantity', compute='_compute_total_delivery_quantity',
                                    default=0)
    invoice_quantity = fields.Float(string='No. Invoiced Quantity', compute='_compute_total_invoiced_quantity',
                                    default=0)

    @api.depends('order_line.product_uom_qty')
    def _compute_total_order_quantity(self):
        for order in self:
            order.order_quantity = sum(order.order_line.mapped('product_uom_qty'))

    @api.depends('order_line.qty_delivered')
    def _compute_total_delivery_quantity(self):
        for order in self:
            order.deliver_quantity = sum(order.order_line.mapped('qty_delivered'))

    @api.depends('order_line.qty_invoiced')
    def _compute_total_invoiced_quantity(self):
        for order in self:
            order.invoice_quantity = sum(order.order_line.mapped('qty_invoiced'))
