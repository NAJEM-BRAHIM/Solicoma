# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritedStockQuant(models.Model):
    _inherit = 'stock.quant'

    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if not self.user_has_groups('odoo_stock_rule_app.group_access_all_location'):
            domain += [("location_id.user_ids", "=", self.env.user.id)]
        return super().search(domain, offset, limit, order, count)

    @api.onchange('location_id')
    def set_domain_location_id(self):
        for rec in self:
            if not rec.user_has_groups('odoo_stock_rule_app.group_access_all_location'):
                domain = {'domain': {'location_id': [("user_ids", "=", self.env.user.id)]}}
                return domain
