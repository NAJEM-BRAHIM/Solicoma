# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    use_virtual_box = fields.Boolean(
        string='Usa Caja Virtual',
        help='Marcar si este producto se gestiona por cajas virtuales.',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    virtual_box = fields.Integer(
        string='Cajas',
        compute='_compute_virtual_box',
    )

    @api.depends_context('location', 'warehouse_id', 'allowed_company_ids')
    @api.depends('stock_quant_ids.virtual_box', 'stock_quant_ids.location_id.usage')
    def _compute_virtual_box(self):
        for product in self:
            product.virtual_box = sum(
                q.virtual_box
                for q in product.stock_quant_ids
                if q.location_id.usage == 'internal'
            )
