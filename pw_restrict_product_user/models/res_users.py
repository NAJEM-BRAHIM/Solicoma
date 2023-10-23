# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    display_type = fields.Selection([
        ('product', 'Product'),
        ('category', 'Category')],
        string='Restriction on', default='product')
    product_ids = fields.Many2many('product.template', string='Products')
    categ_ids = fields.Many2many('product.category', string='Product Categories')

    @api.model_create_multi
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        is_update = False
        for val in vals:
            if 'product_ids' or 'categ_ids' in val:
                is_update = True
        if is_update:
            self.clear_caches()
        return res

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'product_ids' or 'categ_ids' in vals:
            self.clear_caches()
        return res

    @api.onchange('display_type')
    def onchange_display_type(self):
        if self.display_type == 'product':
            self.categ_ids = False
        if self.display_type == 'category':
            self.product_ids = False
