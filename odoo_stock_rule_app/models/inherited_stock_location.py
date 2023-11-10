# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritedStockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many('res.users', 'rel_user_location', 'location_id', 'user_id', string='Accepted Users',
                                tracking=True, copy=False, compute='compute_total_user', store=True)
    own_user_ids = fields.Many2many('res.users', 'rel_own_user_location', 'location_id', 'user_id', string='Own Users',
                                    tracking=True, copy=False)

    @api.depends('location_id', 'own_user_ids')
    def compute_total_user(self):
        own_user_list = []
        new_customers = []
        for record in self:
            for user in record.own_user_ids:
                own_user_list.append(user.id)
            own_user_list = list(set(own_user_list))
            if record.location_id:
                for p_user in record.location_id.own_user_ids:
                    own_user_list.append(p_user.id)
                own_user_list = list(set(own_user_list))
                if record.location_id.location_id:
                    for pp_user in record.location_id.location_id.own_user_ids:
                        own_user_list.append(pp_user.id)
                    own_user_list = list(set(own_user_list))
                    if record.location_id.location_id.location_id:
                        for ppp_user in record.location_id.location_id.location_id.own_user_ids:
                            own_user_list.append(ppp_user.id)
                        own_user_list = list(set(own_user_list))

            record.user_ids = [(6, 0, own_user_list)]

    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if not self.user_has_groups('odoo_stock_rule_app.group_access_all_location'):
            domain += [("user_ids", "=", self.env.user.id)]
        return super().search(domain, offset, limit, order, count)
