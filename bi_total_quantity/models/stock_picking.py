# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
# Fix Sahara Info Services: iteración sobre self para evitar
# "ValueError: Expected singleton" en recomputes por lotes.

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    demand_quantity = fields.Float(string='No. Demand Quantity', compute='_compute_total_demand_quantity')
    done_quantity = fields.Float(string='No. Done Quantity', compute='_compute_total_done_quantity')

    @api.depends('move_ids.product_uom_qty')
    def _compute_total_demand_quantity(self):
        for picking in self:
            picking.demand_quantity = sum(picking.move_ids.mapped('product_uom_qty'))

    @api.depends('move_ids.quantity')
    def _compute_total_done_quantity(self):
        for picking in self:
            picking.done_quantity = sum(picking.move_ids.mapped('quantity'))
