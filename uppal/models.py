# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
import datetime
from datetime import datetime,date,timedelta,time

class sale_order_extension(models.Model):
	_inherit = 'sale.order'

	order_state   = fields.Selection([
		('not_available', 'Not Available'),
		('not_delivered', 'Not Delivered'),
		('invoiced', 'Fully Invoiced'),
		],string="Order State")
	customer_po      = fields.Char(string="Customer PO #")
	inquiry_no       = fields.Char(string="Inquiry No.")
	note_1       = fields.Text(string=" ")
	note_2       = fields.Text(string=" ")
	note_3      = fields.Text(string=" ")
	entity = fields.Many2one('ecube.entity',string="Entity")


	@api.onchange('order_line')
	def change_status(self):
		flag = 0 
		for x in self.order_line:
			if x.product_uom_qty > x.qty_hand:
				flag = 1
		if flag == 1:
			self.order_state = "not_available"
	
class sale_order_line_extension(models.Model):
	_inherit = 'sale.order.line'

	qty_hand      = fields.Float(string="Qty on Hand")
	qty_SO        = fields.Float(string="Qty on SO")
	qty_PO        = fields.Float(string="Qty on PO")
	qty_available = fields.Float(string="Qty Available")
	# testing 			= fields.Many2one('sale.order',string="testing")

	@api.onchange('product_id')
	def all_sales_purchases(self):
		total_sales = self.env['sale.order'].search([('state','=','sale')])
		total_purchase = self.env['purchase.order'].search([('state','=','purchase')])
		stock_history = self.env['stock.history'].search([])

		total = 0
		total_p = 0
		qty_on_hand = 0

		if self.product_id:
			for x in total_sales:
				for y in x.order_line:
					if self.product_id == y.product_id:
						total = total + y.product_uom_qty - y.qty_delivered

			for a in total_purchase:
				for b in a.order_line:
					if self.product_id == b.product_id:
						total_p = total_p + b.product_qty - b.qty_received

			for x in stock_history:
				if self.product_id == x.product_id:
					qty_on_hand = qty_on_hand + x.quantity
	 
		self.qty_SO = total
		self.qty_PO = total_p
		self.qty_hand = qty_on_hand
		self.qty_available = self.qty_hand + self.qty_PO - self.qty_SO


class purchase_order_extension(models.Model):
	_inherit = 'purchase.order'

	order_state   = fields.Selection([
		('not_received', 'Not Received'),
		('invoiced', 'Invoiced'),
		],string="Order State")



class purchase_order_line_extention(models.Model):
	_inherit = 'purchase.order.line'

	qty_received = fields.Float(string="Received Quantity")
	qty_invoiced  = fields.Float(string="Invoiced Qty")
	qty_hand      = fields.Float(string="Qty on Hand")
	qty_SO        = fields.Float(string="Qty on SO")
	qty_PO        = fields.Float(string="Qty on PO")
	qty_available = fields.Float(string="Qty Available")


	@api.onchange('product_id')
	def all_purchases_sales(self):
		total_sales = self.env['sale.order'].search([])
		total_purchase = self.env['purchase.order'].search([])
		stock_history = self.env['stock.history'].search([])

		total = 0
		total_p = 0
		qty_on_hand = 0

		if self.product_id:
			for x in total_sales:
				for y in x.order_line:
					if self.product_id == y.product_id:
						total = total + y.product_uom_qty

			for a in total_purchase:
				for b in a.order_line:
					if self.product_id == b.product_id:
						total_p = total_p + b.product_qty

			for x in stock_history:
				if self.product_id == x.product_id:
					qty_on_hand = qty_on_hand + x.quantity
	 
		self.qty_SO = total
		self.qty_PO = total_p
		self.qty_hand = qty_on_hand
		self.qty_available = self.qty_PO - self.qty_SO





class stock_picking_own(models.Model):
	_inherit 	= 'stock.picking'

	def do_new_transfer(self):
		new_record = super(stock_picking_own, self).do_new_transfer()
		sale_order = self.env['sale.order'].search([('name','=',self.origin)])
		purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])

		flag = 0 
		flag_p = 0

		for x in self.pack_operation_product_ids:
			if sale_order:
				if x.qty_done < x.product_qty:
					sale_order.order_state = "not_delivered"
					flag = 1
			if purchase_order:
				if x.qty_done < x.product_qty:
					purchase_order.order_state = "not_received"
					flag_p = 1

		if sale_order and flag == 0:
			sale_order.order_state = "invoiced"
		if purchase_order and flag_p == 0:
			purchase_order.order_state = "invoiced"
	
		return new_record


class sale_order_extension(models.Model):
	_name = 'ecube.entity'

	name = fields.Char(string="Name")


class customer_extension(models.Model):
	_inherit = 'res.partner'


	ntn = fields.Char('NTN')
	sale_tax_reg = fields.Char('Sales Tax Reg')
	sale_tax_chk = fields.Char('Sales Tax')
