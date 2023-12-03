# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class SaleMultiWarehouse(models.TransientModel):
	_name = "sale.multi.warehouse"
	_description = "Sale Multi Warehouse"


	product_id = fields.Many2one('product.product',string="Product")
	product_qty = fields.Float(string='Quantity')
	so_warehouse_line = fields.One2many('sale.multi.warehouse.line','sale_warehouse_id',string="SO Warehouse Lines")


	@api.model
	def default_get(self,fields):
		res = super(SaleMultiWarehouse, self).default_get(fields)
		context = dict(self._context or {})
		active_ids = context.get('active_ids')
		sale_order_id = self.env['sale.order'].browse(active_ids)
		order_ids = self.env['sale.order.line'].browse(self._context.get('active_id'))
		product_id = order_ids.product_id
		res['product_id'] = product_id.id
		res['product_qty'] = order_ids.product_uom_qty
		warehouse_data = {}
		location_ids = self.env['stock.location'].search([('usage','=','internal')])
		for location_id in location_ids:
			warehouse_short_code = location_id.display_name.split("/")[0]
			warehouse_id = self.env['stock.warehouse'].search([('code','=',warehouse_short_code)],limit=1)				
			quant_ids = self.env['stock.quant'].search([('product_id','=',product_id.id),('location_id','=',location_id.id)])
			if warehouse_id in warehouse_data.keys():
				s_warehouse_data = warehouse_data[warehouse_id]
				s_warehouse_data.update({
					'on_hand': s_warehouse_data['on_hand'] + sum(quant_id.quantity for quant_id in quant_ids),
					'available_qty': s_warehouse_data['available_qty'] + sum(quant_id.available_quantity for quant_id in quant_ids)
				})
			else:
				warehouse_data.update({
					warehouse_id:{
						'on_hand':sum(quant_id.quantity for quant_id in quant_ids),
						'available_qty':sum(quant_id.available_quantity for quant_id in quant_ids)
					}
				})
		lines = []
		for warehouse_id in warehouse_data:
			lines.append({
				'warehouse_id':warehouse_id.id,
				'pro_warehouse_id' : warehouse_id.id,
				'product_uom' : order_ids.product_uom.id,
				'pro_uom' :  order_ids.product_uom.id,
				'available_qty':warehouse_data[warehouse_id]['available_qty'],
				'pro_available_qty' : warehouse_data[warehouse_id]['available_qty'],
			})
		res.update({'so_warehouse_line':[(0,0,line_val)for line_val in lines]})
		return res
		

	def action_confirm_details(self):
		order_line_id = self.env['sale.order.line'].browse(self._context.get('active_id'))
		line_list = []
		for order in self:
			if order.so_warehouse_line:
				for line in self.so_warehouse_line:
					if line.custom_quantity > 0:
						line_list.append([0, 0, {
							'product_id': order.product_id.id,
							'so_warehouse_id': line.pro_warehouse_id.id,
							'so_product_uom' : line.pro_uom.id,
							'quantity' : line.custom_quantity,
							'sale_order_id': order_line_id.order_id.id
						}])

				order_line_id.order_id.update({'custom_warehouse_line': line_list})



class SaleMultiWarehouseLine(models.TransientModel):
	_name = "sale.multi.warehouse.line"
	_description = "Sale Multi Warehouse Line"

	custom_quantity = fields.Float(string="Quantity")
	on_hand = fields.Float('On Hand Qty')
	pro_warehouse_id = fields.Many2one('stock.warehouse' , string="Pro Warehouse")
	warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse" , related="pro_warehouse_id")
	pro_available_qty = fields.Float(string='Pro Available Qty')
	available_qty = fields.Float(string='Available Qty' , related='pro_available_qty')
	pro_uom = fields.Many2one('uom.uom', string="Pro UOM")
	product_uom = fields.Many2one('uom.uom', string='Unit of Measure' , related="pro_uom")
	sale_warehouse_id = fields.Many2one('sale.multi.warehouse',string="Sale MultiWarehouse")


	@api.onchange('custom_quantity')
	def check_quantity(self):
		for record in self:
			if record.custom_quantity > record.sale_warehouse_id.product_qty:
				warning = {
					'title': _('Validation Error'),
					'message':
						_("Product total quantity can not be greater than custom quantity.")}
				return {'warning': warning}
