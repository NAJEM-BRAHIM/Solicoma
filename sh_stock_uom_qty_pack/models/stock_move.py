# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

class ShStockMove(models.Model):
    _inherit = "stock.move"

    sh_bag_qty = fields.Integer("Bag Quantity")
    sh_qty_in_bag = fields.Float(
        related="product_id.sh_qty_in_bag", string="Quantity in Bag")

    @api.onchange("sh_bag_qty")
    def onchange_product_uom_qty(self):
        if self and self.sh_bag_qty > 0:
            self.product_uom_qty = self.sh_bag_qty * self.product_id.sh_qty_in_bag
