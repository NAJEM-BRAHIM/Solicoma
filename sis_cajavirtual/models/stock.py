# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from collections import defaultdict, namedtuple

from odoo import api, fields, models, tools, _
from odoo.tools import html_escape

from odoo.exceptions import UserError, ValidationError
from odoo.tools import OrderedSet
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

import logging
_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    virtual_box = fields.Integer('Cajas')

    """
    @api.model_create_multi
    def create(self, vals_list):
        virtual_box = False
        for vals in vals_list:
            _logger.info('stock move line: %s'%vals)
            if vals.get('move_id'):
                vals['virtual_box'] = self.env['stock.move'].browse(vals.get('move_id')).virtual_box
                virtual_box = True
        if virtual_box:
            mls = super(StockMoveLine, self.with_context(set_virtual_box=vals['virtual_box'])).create(vals_list)    
        else:
            mls = super(StockMoveLine, self).create(vals_list)       
        return mls
        """

    def _get_aggregated_product_quantities(self, **kwargs):

        def get_aggregated_properties(move_line=False, move=False):
            move = move or move_line.move_id
            uom = move_line and move_line.product_uom_id or move.product_uom
            name = move.product_id.display_name
            description = move.description_picking
            if description == name or description == move.product_id.name:
                description = False
            product = move.product_id
            line_key = f'{product.id}_{product.display_name}_{description or ""}_{uom.id}'
            return (line_key, name, description, uom)

        aggregated_move_lines = super(StockMoveLine,self)._get_aggregated_product_quantities(**kwargs)
        for move_line in self:
            line_key, name, description, uom = get_aggregated_properties(move_line=move_line)
            if line_key in aggregated_move_lines:                        
                _logger.info("virtual_box: %s => %s (%s)"%(move_line.display_name,move_line.move_id.virtual_box,move_line.qty_done))
                aggregated_move_lines[line_key]['virtual_box'] = move_line.move_id.virtual_box
                _logger.info("simple: %s => %s"%(line_key,aggregated_move_lines[line_key]))
        return aggregated_move_lines         

    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """
        Quant = self.env['stock.quant']

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_ids_tracked_without_lot = OrderedSet()
        ml_ids_to_delete = OrderedSet()
        ml_ids_to_create_lot = OrderedSet()
        for ml in self:
            # Check here if `ml.qty_done` respects the rounding of `ml.product_uom_id`.
            uom_qty = float_round(ml.qty_done, precision_rounding=ml.product_uom_id.rounding, rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_done = float_round(ml.qty_done, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, qty_done, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%s" doesn\'t respect the rounding precision \
                                  defined on the unit of measure "%s". Please change the quantity done or the \
                                  rounding precision of your unit of measure.') % (ml.product_id.display_name, ml.product_uom_id.name))

            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking != 'none':
                    picking_type_id = ml.move_id.picking_type_id
                    if picking_type_id:
                        if picking_type_id.use_create_lots:
                            # If a picking type is linked, we may have to create a production lot on
                            # the fly before assigning it to the move line if the user checked both
                            # `use_create_lots` and `use_existing_lots`.
                            if ml.lot_name and not ml.lot_id:
                                lot = self.env['stock.lot'].search([
                                    ('company_id', '=', ml.company_id.id),
                                    ('product_id', '=', ml.product_id.id),
                                    ('name', '=', ml.lot_name),
                                ], limit=1)
                                if lot:
                                    ml.lot_id = lot.id
                                else:
                                    ml_ids_to_create_lot.add(ml.id)
                        elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                            # If the user disabled both `use_create_lots` and `use_existing_lots`
                            # checkboxes on the picking type, he's allowed to enter tracked
                            # products without a `lot_id`.
                            continue
                    elif ml.is_inventory:
                        # If an inventory adjustment is linked, the user is allowed to enter
                        # tracked products without a `lot_id`.
                        continue

                    if not ml.lot_id and ml.id not in ml_ids_to_create_lot:
                        ml_ids_tracked_without_lot.add(ml.id)
            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            elif not ml.is_inventory:
                ml_ids_to_delete.add(ml.id)

        if ml_ids_tracked_without_lot:
            mls_tracked_without_lot = self.env['stock.move.line'].browse(ml_ids_tracked_without_lot)
            raise UserError(_('You need to supply a Lot/Serial Number for product: \n - ') +
                              '\n - '.join(mls_tracked_without_lot.mapped('product_id.display_name')))
        ml_to_create_lot = self.env['stock.move.line'].browse(ml_ids_to_create_lot)
        ml_to_create_lot._create_and_assign_production_lot()

        mls_to_delete = self.env['stock.move.line'].browse(ml_ids_to_delete)
        mls_to_delete.unlink()

        mls_todo = (self - mls_to_delete)
        mls_todo._check_company()

        # Now, we can actually move the quant.
        ml_ids_to_ignore = OrderedSet()
        for ml in mls_todo:
            if ml.product_id.type == 'product':
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml.move_id._should_bypass_reservation(ml.location_id) and float_compare(ml.qty_done, ml.reserved_uom_qty, precision_rounding=rounding) > 0:
                    qty_done_product_uom = ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id, rounding_method='HALF-UP')
                    extra_qty = qty_done_product_uom - ml.reserved_qty
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, ml_ids_to_ignore=ml_ids_to_ignore)
                # unreserve what's been reserved
                if not ml.move_id._should_bypass_reservation(ml.location_id) and ml.product_id.type == 'product' and ml.reserved_qty:
                    try:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.reserved_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.reserved_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, virtual_box=-ml.move_id.virtual_box)
                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, virtual_box=-ml.move_id.virtual_box)
                        Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, virtual_box=ml.move_id.virtual_box)
                Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id, package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date, virtual_box=ml.move_id.virtual_box)
            ml_ids_to_ignore.add(ml.id)
        # Reset the reserved quantity as we just moved it to the destination location.
        mls_todo.with_context(bypass_reservation_update=True).write({
            'reserved_uom_qty': 0.00,
            'date': fields.Datetime.now(),
        })        


class StockMove(models.Model):

    _inherit = 'stock.move'

    virtual_box = fields.Integer('Cajas')

    def _prepare_procurement_values(self):
        res = super(StockMove,self)._prepare_procurement_values()
        res['virtual_box'] = self.virtual_box
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):        
        res = super(StockMove,self)._prepare_move_line_vals(quantity, reserved_quant)
        _logger.info('result: %s'%res)
        res['virtual_box'] = self.virtual_box
        return res

    """

    @api.model
    def create(self, vals):
        virtual_box = False
        if 'sale_line_id' in vals:
            line_id = vals['sale_line_id']
            sale_line_id = self.env['sale.order.line'].search([('id','=',line_id)])
            if sale_line_id:
                vals['virtual_box'] = sale_line_id.virtual_box
                virtual_box = True
        if virtual_box:
            res = super(StockMove, self.with_context(set_virtual_box=vals['virtual_box'])).create(vals)
        else:                
            res = super(StockMove, self).create(vals)
        return res        
    """

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _run_push(self, move):
        """ Apply a push rule on a move.
        If the rule is 'no step added' it will modify the destination location
        on the move.
        If the rule is 'manual operation' it will generate a new move in order
        to complete the section define by the rule.
        Care this function is not call by method run. It is called explicitely
        in stock_move.py inside the method _push_apply
        """
        self.ensure_one()
        new_date = fields.Datetime.to_string(move.date + relativedelta(days=self.delay))
        if self.auto == 'transparent':
            old_dest_location = move.location_dest_id
            move.write({'date': new_date, 'location_dest_id': self.location_id.id})
            # make sure the location_dest_id is consistent with the move line location dest
            if move.move_line_ids:
                move.move_line_ids.location_dest_id = move.location_dest_id._get_putaway_strategy(move.product_id) or move.location_dest_id

            # avoid looping if a push rule is not well configured; otherwise call again push_apply to see if a next step is defined
            if self.location_id != old_dest_location:
                # TDE FIXME: should probably be done in the move model IMO
                return move._push_apply()[:1]
        else:
            new_move_vals = self._push_prepare_move_copy_values(move, new_date)
            new_move = move.sudo().copy(new_move_vals)
            if new_move._should_bypass_reservation():
                new_move.write({'procure_method': 'make_to_stock'})
            if not new_move.location_id.should_bypass_reservation():
                move.write({'move_dest_ids': [(4, new_move.id)]})
            return new_move
   
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'pull' or 'pull_push') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
        group_id = False
        if self.group_propagation_option == 'propagate':
            group_id = values.get('group_id', False) and values['group_id'].id
        elif self.group_propagation_option == 'fixed':
            group_id = self.group_id.id

        date_scheduled = fields.Datetime.to_string(
            fields.Datetime.from_string(values['date_planned']) - relativedelta(days=self.delay or 0)
        )
        date_deadline = values.get('date_deadline') and (fields.Datetime.to_datetime(values['date_deadline']) - relativedelta(days=self.delay or 0)) or False
        partner = self.partner_address_id or (values.get('group_id', False) and values['group_id'].partner_id)
        if partner:
            product_id = product_id.with_context(lang=partner.lang or self.env.user.lang)
        picking_description = product_id._get_description(self.picking_type_id)
        if values.get('product_description_variants'):
            picking_description += values['product_description_variants']
        # it is possible that we've already got some move done, so check for the done qty and create
        # a new move with the correct qty
        qty_left = product_qty

        move_dest_ids = []
        if not self.location_id.should_bypass_reservation():
            move_dest_ids = values.get('move_dest_ids', False) and [(4, x.id) for x in values['move_dest_ids']] or []

        # when create chained moves for inter-warehouse transfers, set the warehouses as partners
        if not partner and move_dest_ids:
            move_dest = values['move_dest_ids']
            if location_id == company_id.internal_transit_location_id:
                partners = move_dest.location_dest_id.warehouse_id.partner_id
                if len(partners) == 1:
                    partner = partners
                    move_dest.partner_id = partner

        move_values = {
            'name': name[:2000],
            'company_id': self.company_id.id or self.location_src_id.company_id.id or self.location_id.company_id.id or company_id.id,
            'product_id': product_id.id,
            'product_uom': product_uom.id,
            'product_uom_qty': qty_left,
            'partner_id': partner.id if partner else False,
            'location_id': self.location_src_id.id,
            'location_dest_id': location_id.id,
            'move_dest_ids': move_dest_ids,
            'rule_id': self.id,
            'procure_method': self.procure_method,
            'origin': origin,
            'picking_type_id': self.picking_type_id.id,
            'group_id': group_id,
            'route_ids': [(4, route.id) for route in values.get('route_ids', [])],
            'warehouse_id': self.propagate_warehouse_id.id or self.warehouse_id.id,
            'date': date_scheduled,
            'date_deadline': False if self.group_propagation_option == 'fixed' else date_deadline,
            'propagate_cancel': self.propagate_cancel,
            'description_picking': picking_description,
            'priority': values.get('priority', "0"),
            'orderpoint_id': values.get('orderpoint_id') and values['orderpoint_id'].id,
            'product_packaging_id': values.get('product_packaging_id') and values['product_packaging_id'].id,
            'virtual_box': values.get('virtual_box', 0),
        }
        for field in self._get_custom_move_fields():
            if field in values:
                move_values[field] = values.get(field)
        return move_values    

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

class StockQuant(models.Model):

    _inherit = 'stock.quant'

    virtual_box = fields.Integer('Cajas')

    """
    @api.model
    def create(self, vals):
        if self.env.context.get('set_virtual_box'):
            vals['virtual_box'] = self.env.context.get('set_virtual_box')
        res = super(StockQuant, self).create(vals)
        return res
        """

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None, virtual_box=False):
        """ Increase or decrease `reserved_quantity` of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :param datetime in_date: Should only be passed when calls to this method are done in
                                 order to move a quant. When creating a tracked quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)

        incoming_dates = [d for d in quants.mapped('in_date') if d]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = min(incoming_dates)
        else:
            in_date = fields.Datetime.now()

        quant = None
        if quants:
            # see _acquire_one_job for explanations
            self._cr.execute("SELECT id FROM stock_quant WHERE id IN %s LIMIT 1 FOR NO KEY UPDATE SKIP LOCKED", [tuple(quants.ids)])
            stock_quant_result = self._cr.fetchone()
            if stock_quant_result:
                quant = self.browse(stock_quant_result[0])

        if quant:
            quant.write({
                'quantity': quant.quantity + quantity,
                'in_date': in_date,
                'virtual_box': quant.virtual_box + virtual_box                
            })
        else:
            self.create({
                'product_id': product_id.id,
                'location_id': location_id.id,
                'quantity': quantity,
                'lot_id': lot_id and lot_id.id,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
                'virtual_box': virtual_box
            })
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=False, allow_negative=True), in_date
