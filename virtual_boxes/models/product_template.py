# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    use_virtual_box = fields.Boolean(
        string='Usa cajas virtuales',
        help='Activa el control de número de cajas para este artículo'
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    use_virtual_box = fields.Boolean(
        related='product_tmpl_id.use_virtual_box',
        store=True,
    )
