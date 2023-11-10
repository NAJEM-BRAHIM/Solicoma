# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritedStockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if not self.user_has_groups('odoo_stock_rule_app.group_access_all_location'):
            domain += '|'
            domain += [("default_location_src_id.user_ids", "=", self.env.user.id)]
            domain += [("default_location_dest_id.user_ids", "=", self.env.user.id)]
        return super().search(domain, offset, limit, order, count)
