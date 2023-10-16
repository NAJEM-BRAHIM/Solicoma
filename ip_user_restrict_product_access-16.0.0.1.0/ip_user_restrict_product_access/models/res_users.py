# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    type_of_product = fields.Selection([
        ('product_wise', 'Products'),
        ('category_wise', 'Product Categories')],
        string='Restriction By',
        default='product_wise',
        help='Products: Restrict User to give access to selected Product.\n'
             'Product Categories: Restrict User to give access to selected Product Categories.')
    product_ids = fields.Many2many('product.product', string="Allowed Products", help='Allows user to access those Product which are Selected hear.')
    categ_ids = fields.Many2many('product.category', string="Allowed Category", help='Allows all Product of Selected Categorys.')

    @api.onchange('type_of_product')
    def _onchange_type_of_product(self):
        if self.type_of_product != 'product_wise':
            self.product_ids = False
        if self.type_of_product != 'category_wise':
            self.categ_ids = False

    @api.onchange('categ_ids')
    def onchange_categ_ids(self):
        self.product_ids = False
        if self.categ_ids:
            self.product_ids = self.env['product.product'].search(['|', ('categ_id', 'in', self.categ_ids.ids), ('categ_id', 'child_of', self.categ_ids.ids)])

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'type_of_product' in vals or 'product_ids' in vals or 'categ_ids' in vals:
            self.env.registry._clear_cache()
        return res
