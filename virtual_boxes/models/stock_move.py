# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    # Total indicativo desde el pedido de venta.
    # Las cajas reales por lote se introducen en stock.move.line.
    num_boxes = fields.Integer(
        string='Nº Cajas',
        compute='_compute_num_boxes',
        store=True,
        readonly=False,
    )
    use_virtual_box = fields.Boolean(related='product_id.use_virtual_box', store=False)

    @api.depends('sale_line_id.num_boxes', 'product_id.use_virtual_box')
    def _compute_num_boxes(self):
        for move in self:
            if move.sale_line_id and move.product_id.use_virtual_box:
                move.num_boxes = move.sale_line_id.num_boxes
            else:
                move.num_boxes = 0

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        self._update_quant_num_boxes()
        return res

    def _update_quant_num_boxes(self):
        """Actualiza Nº Cajas en stock.quant por lote al validar el movimiento."""
        StockQuant = self.env['stock.quant'].sudo()
        for move in self.filtered(lambda m: m.product_id.use_virtual_box):
            for ml in move.move_line_ids.filtered(lambda l: l.num_boxes):
                # Sumar cajas en ubicación destino (interna)
                if ml.location_dest_id.usage == 'internal':
                    quant = StockQuant.search([
                        ('product_id', '=', ml.product_id.id),
                        ('location_id', '=', ml.location_dest_id.id),
                        ('lot_id', '=', ml.lot_id.id if ml.lot_id else False),
                    ], limit=1)
                    if quant:
                        quant.write({'num_boxes': quant.num_boxes + ml.num_boxes})

                # Restar cajas de ubicación origen (interna)
                if ml.location_id.usage == 'internal':
                    quant = StockQuant.search([
                        ('product_id', '=', ml.product_id.id),
                        ('location_id', '=', ml.location_id.id),
                        ('lot_id', '=', ml.lot_id.id if ml.lot_id else False),
                    ], limit=1)
                    if quant:
                        quant.write({'num_boxes': quant.num_boxes - ml.num_boxes})
