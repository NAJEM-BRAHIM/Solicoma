# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritedResUsers(models.Model):
    _inherit = 'res.users'

    location_ids = fields.Many2many('stock.location', 'rel_location_user', 'user_id', 'location_id',
                                    string='Location',
                                     copy=False, compute='compute_total_location')

    def compute_total_location(self):
        loc_list = []
        for rec in self:
            location_ids = self.env['stock.location'].search([('user_ids', '=', rec.id)])
            for location_id in location_ids:
                loc_list.append(location_id.id)
            loc_list = list(set(loc_list))
            rec.location_ids = [(6, 0, loc_list)]
