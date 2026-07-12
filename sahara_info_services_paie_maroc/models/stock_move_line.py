# -*- coding: utf-8 -*-
from odoo import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_lines = super()._get_aggregated_product_quantities(**kwargs)
        for line in aggregated_lines:
            aggregated_lines[line]['virtual_box'] = 1
        return aggregated_lines
