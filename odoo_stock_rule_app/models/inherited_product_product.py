from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round


class InheritedProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            date_date_expected_domain_from = [
                '|',
                '&',
                ('state', '=', 'done'),
                ('date', '>=', from_date),
                '&',
                ('state', '!=', 'done'),
                ('forecast_expected_date', '>=', from_date),
            ]
            domain_move_in += date_date_expected_domain_from
            domain_move_out += date_date_expected_domain_from
        if to_date:
            date_date_expected_domain_to = [
                '|',
                '&',
                ('state', '=', 'done'),
                ('date', '<=', to_date),
                '&',
                ('state', '!=', 'done'),
                ('forecast_expected_date', '<=', to_date),
            ]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'in',
                                ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in',
                                 ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in
                            Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
                                            orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in
                             Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'],
                                             orderby='id'))
        quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in
                          Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'],
                                           ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                     Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                                                     orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                      Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
                                                      ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            if not product_id:
                res[product_id] = dict.fromkeys(
                    ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
                    0.0,
                )
                continue
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if self.user_has_groups('odoo_stock_rule_app.group_access_all_location'):
                if dates_in_the_past:
                    qty_available = quants_res.get(product_id, [0.0])[0] - moves_in_res_past.get(product_id,
                                                                                                 0.0) + moves_out_res_past.get(
                        product_id, 0.0)
                else:
                    qty_available = quants_res.get(product_id, [0.0])[0]
                reserved_quantity = quants_res.get(product_id, [False, 0.0])[1]
                res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
                res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity,
                                                          precision_rounding=rounding)
                res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
                                                              precision_rounding=rounding)
                res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
                                                              precision_rounding=rounding)
                res[product_id]['virtual_available'] = float_round(
                    qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                    precision_rounding=rounding)
            else:
                qty_available = 0
                reserved_quantity = 0
                for rec in self:
                    location_ids = rec.env['stock.location'].search([('user_ids', '=', rec.env.user.id)])
                    quant_ids = rec.env['stock.quant'].search(
                        [('product_id', '=', rec.id), ('location_id', 'in', location_ids.ids)])
                    for quant_id in quant_ids:
                        qty_available += quant_id.quantity
                        reserved_quantity += quant_id.reserved_quantity
                    res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
                    res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity,
                                                              precision_rounding=rounding)
                    res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
                                                                  precision_rounding=rounding)
                    res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
                                                                  precision_rounding=rounding)
                    res[product_id]['virtual_available'] = float_round(
                        qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                        precision_rounding=rounding)

        return res
