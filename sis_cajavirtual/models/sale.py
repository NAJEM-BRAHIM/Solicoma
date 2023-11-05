# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools import float_compare

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    virtual_box = fields.Integer('Boxes')

    def _prepare_invoice_line(self, **optional_values):    
        result = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        result.update({
            'virtual_box': self.virtual_box
            })        
        return result

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({'virtual_box':self.virtual_box})
        return values

    #def _action_launch_stock_rule(self, previous_product_uom_qty=False):
    #    return super()._action_launch_stock_rule(previous_product_uom_qty)
    
    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            procurements.append(self.env['procurement.group'].Procurement(
                line.product_id, product_qty, procurement_uom,
                line.order_id.partner_shipping_id.property_stock_customer,
                line.name, line.order_id.name, line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)

        # This next block is currently needed only because the scheduler trigger is done by picking confirmation rather than stock.move confirmation
        orders = self.mapped('order_id')
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
        return True        


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    """
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        if 'state' in values and self.state=='sale':
            for order in self:      
                _logger.info('Order: %s'%order.name)      
                if order.order_line:                    
                    _logger.info('Order Line: %s'%order.order_line)      
                    for line in order.order_line:
                        _logger.info('Line: %s'%line)      
                        move_ids = self.env['stock.move'].search([('sale_line_id','=',line.id)])
                        _logger.info('Move_ids: %s'%move_ids)
                        for move in move_ids:
                            _logger.info('Move: %s-%s'%(move.name,move.state))
                            move.write({'virtual_box':line.virtual_box})
        return res
        """