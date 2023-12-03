# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import float_is_zero, float_compare


class SaleOrder(models.Model):
	_inherit= "sale.order"

	custom_warehouse_line = fields.One2many('multi.warehouse.line', 'sale_order_id' , string="warehouse")
	delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_count')
	

	def _compute_count(self):
		for order in self:
			picking = self.env['stock.picking'].search([('origin', '=', order.name)])
			order.delivery_count = len(picking)

	def action_delivery(self):
		for order in self:
			return{
				'name': 'Delivery',
				'res_model': 'stock.picking',
				'domain': [('origin', '=', order.name)],
				'view_mode': 'tree,form',
				'type': 'ir.actions.act_window',
				'context': "{'create': False}"
			}

	def action_confirm(self):
		order_id = self.env['sale.order'].browse(self.id)
		if self.env.user.has_group('sale_order_line_multi_warhouse_app.group_show_sale_order_product_details'):
			for line in order_id.custom_warehouse_line:
				location_id = line.so_warehouse_id.lot_stock_id
				location_dest_id = order_id.partner_id.property_stock_customer

				if line.product_id.type != 'service':
					picking_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders'),
																		  ('warehouse_id', '=', order_id.warehouse_id.id)])
					picking = self.env['stock.picking'].create({'partner_id': order_id.partner_id.id,
														  'scheduled_date': datetime.now(),
														  'location_id': location_id.id,
														  'location_dest_id':location_dest_id.id,
														  'picking_type_id': picking_type.id,
														  'origin': order_id.name,
														  'move_ids_without_package': [[0, 0, {
																			'product_id': line.product_id.id,
																			'product_uom_qty': line.quantity,
																			'name': line.product_id.id,
																			'product_uom': line.so_product_uom.id,
																			'location_id': location_id.id,
																			'location_dest_id': location_dest_id.id}]]
																})

					picking.sudo().write({'state': 'assigned'})
			order_id.write({
					'state': 'sale',
					'date_order': fields.Datetime.now()
				})
		return True


class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	
class Multiwarehouseline(models.Model):
	_name = 'multi.warehouse.line'
	_description = 'Multiwarehouse line'

	product_id = fields.Many2one('product.product',string="Product")
	so_warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse")
	so_product_uom = fields.Many2one('uom.uom', string="Unit Of Measure")
	quantity = fields.Float(string="Quantity")
	sale_order_id = fields.Many2one('sale.order' , string="Sale")