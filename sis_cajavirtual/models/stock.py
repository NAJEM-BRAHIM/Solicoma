# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    virtual_box = fields.Integer(string='Cajas')

    def _get_aggregated_product_quantities(self, **kwargs):
        """Extend aggregation result with virtual_box from move."""
        result = super()._get_aggregated_product_quantities(**kwargs)
        for line in self:
            if not line.move_id or not line.move_id.virtual_box:
                continue
            props = self._get_aggregated_properties(move_line=line)
            line_key = props["line_key"]
            if line_key in result:
                result[line_key].setdefault("virtual_box", 0)
                result[line_key]["virtual_box"] += line.move_id.virtual_box
        return result

    def _synchronize_quant(self, quantity, location, action="available", in_date=False, **quants_value):
        """Intercept quant sync to propagate virtual_box from the move."""
        virtual_box = self.move_id.virtual_box or 0
        if virtual_box and action == 'available' and not self.product_uom_id.is_zero(quantity):
            # negative quantity = removing from source → remove boxes
            # positive quantity = adding to destination → add boxes
            sign = 1 if quantity > 0 else -1
            ctx = dict(self.env.context, _sis_virtual_box_delta=sign * virtual_box)
            return super(StockMoveLine, self.with_context(ctx))._synchronize_quant(
                quantity, location, action, in_date, **quants_value
            )
        return super()._synchronize_quant(quantity, location, action, in_date, **quants_value)


class StockMove(models.Model):
    _inherit = 'stock.move'

    virtual_box = fields.Integer(string='Cajas')

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res['virtual_box'] = self.virtual_box
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super()._prepare_move_line_vals(quantity, reserved_quant)
        res['virtual_box'] = self.virtual_box
        return res


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        move_values = super()._get_stock_move_values(
            product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values
        )
        move_values['virtual_box'] = values.get('virtual_box', 0)
        return move_values


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    virtual_box = fields.Integer(string='Cajas')

    @api.model
    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity=False,
        reserved_quantity=False,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
        virtual_box=0,
    ):
        """Override to accept and persist virtual_box alongside quantity updates."""
        # Accept virtual_box from context (set by StockMoveLine._synchronize_quant)
        virtual_box = virtual_box or self.env.context.get('_sis_virtual_box_delta', 0)

        if not (quantity or reserved_quantity):
            raise ValidationError(_('Quantity or Reserved Quantity should be set.'))

        self = self.sudo()
        quants = self._gather(
            product_id, location_id,
            lot_id=lot_id, package_id=package_id, owner_id=owner_id,
            strict=True,
        )
        if lot_id:
            if product_id.uom_id.compare(quantity, 0) > 0:
                quants = quants.filtered(lambda q: q.lot_id)
            else:
                quants = quants.filtered(
                    lambda q: product_id.uom_id.compare(q.quantity, 0) > 0 or q.lot_id
                )

        if location_id.should_bypass_reservation():
            incoming_dates = []
        else:
            incoming_dates = [
                quant.in_date for quant in quants
                if quant.in_date and quant.product_uom_id.compare(quant.quantity, 0) > 0
            ]
        if in_date:
            incoming_dates += [in_date]
        in_date = min(incoming_dates) if incoming_dates else fields.Datetime.now()

        quant = None
        if quants:
            quant = quants.try_lock_for_update(allow_referencing=True, limit=1)

        if quant:
            vals = {'in_date': in_date}
            if quantity:
                vals['quantity'] = quant.quantity + quantity
            if reserved_quantity:
                vals['reserved_quantity'] = max(0, quant.reserved_quantity + reserved_quantity)
            if virtual_box:
                vals['virtual_box'] = (quant.virtual_box or 0) + virtual_box
            quant.write(vals)
        else:
            vals = {
                'product_id': product_id.id,
                'location_id': location_id.id,
                'lot_id': lot_id and lot_id.id,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
            }
            if quantity:
                vals['quantity'] = quantity
            if reserved_quantity:
                vals['reserved_quantity'] = reserved_quantity
            if virtual_box:
                vals['virtual_box'] = virtual_box
            self.create(vals)

        return (
            self._get_available_quantity(
                product_id, location_id,
                lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                strict=True, allow_negative=True,
            ),
            in_date,
        )

    @api.model
    def _get_inventory_fields_write(self):
        """Allow virtual_box to be edited in inventory adjustment."""
        res = super()._get_inventory_fields_write()
        res += ['virtual_box']
        return res
