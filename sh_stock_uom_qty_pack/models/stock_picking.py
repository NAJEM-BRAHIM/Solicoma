# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields

class StockPicking(models.Model):

    _inherit = "stock.picking"

    sh_enable_quantity = fields.Boolean(
        "Enable Quantity", related="company_id.sh_show_bag_size_stock_move_ids")
    sh_enable_quantity_in_report = fields.Boolean(
        "Enable Quantity In Report", related="company_id.sh_show_bag_size_in_stock_report"
    )
