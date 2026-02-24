# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id', 'picking_type_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.price_unit = rec.product_id.standard_price

    def _get_value_data(
        self,
        forced_std_price=False,
        at_date=False,
        ignore_manual_update=False,
        add_extra_value=True,
    ):
        self.ensure_one()
        if self.is_in and self.price_unit:
            valued_qty = self._get_valued_qty()
            value = self.price_unit * valued_qty
            return {
                'value': value,
                'quantity': valued_qty,
                'description': "Valued at receipt price",
            }

        result = super(StockMove,self)._get_value_data(
            forced_std_price=forced_std_price,
            at_date=at_date,
            ignore_manual_update=ignore_manual_update,
            add_extra_value=add_extra_value,
        )
        return result
   
