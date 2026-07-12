# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    num_boxes = fields.Integer(
        string='Nº Cajas',
        compute='_compute_num_boxes',
        store=True,
        readonly=False,
        help='Cajas para este lote. Se calcula proporcionalmente al total del movimiento.',
    )
    use_virtual_box = fields.Boolean(related='product_id.use_virtual_box', store=False)

    @api.depends('move_id.num_boxes', 'quantity', 'move_id.product_uom_qty', 'product_id.use_virtual_box')
    def _compute_num_boxes(self):
        for line in self:
            move = line.move_id
            if move.num_boxes and move.product_uom_qty and line.product_id.use_virtual_box:
                ratio = (line.quantity or 0) / move.product_uom_qty if move.product_uom_qty else 0
                line.num_boxes = round(move.num_boxes * ratio)
            else:
                line.num_boxes = 0

    def _get_aggregated_product_quantities(self, **kwargs):
        """Añade num_boxes al diccionario de líneas agrupadas para el albarán impreso."""
        aggregated = super()._get_aggregated_product_quantities(**kwargs)
        for move_line in self:
            aggregated_properties = self._get_aggregated_properties(move_line=move_line)
            line_key = aggregated_properties['line_key']
            if line_key in aggregated:
                aggregated[line_key]['num_boxes'] = (
                    aggregated[line_key].get('num_boxes', 0) + move_line.num_boxes
                )
        return aggregated
