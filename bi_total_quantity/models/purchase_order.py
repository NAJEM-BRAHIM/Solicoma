# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
# Fix Sahara Info Services: iteración sobre self para evitar
# "ValueError: Expected singleton" en recomputes por lotes.

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_quantity = fields.Float(string='No. Ordered Quantity', compute='_compute_total_purchase_quantity')
    received_quantity = fields.Float(string='No. Received Quantity', compute='_compute_total_received_quantity')
    bill_quantity = fields.Float(string='No. Billed Quantity', compute='_compute_total_bill_quantity')

    @api.depends('order_line.product_qty')
    def _compute_total_purchase_quantity(self):
        for order in self:
            order.purchase_quantity = sum(order.order_line.mapped('product_qty'))

    @api.depends('order_line.qty_received')
    def _compute_total_received_quantity(self):
        for order in self:
            order.received_quantity = sum(order.order_line.mapped('qty_received'))

    @api.depends('order_line.qty_invoiced')
    def _compute_total_bill_quantity(self):
        for order in self:
            order.bill_quantity = sum(order.order_line.mapped('qty_invoiced'))
