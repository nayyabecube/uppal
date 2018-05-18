# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BillofMaterialTree(models.Model): 
	_inherit = 'mrp.bom.line'

	cost = fields.Float(string="Cost")
	total_cost = fields.Float(string="Total Cost")

	@api.onchange('product_id')
	def onchange_product(self):
		if self.product_id:
			current_prod = self.env['product.product'].search([('id','=',self.product_id.id)])
			self.cost = current_prod.standard_price

	@api.onchange('cost')
	def onchange_cost(self):
		if self.cost:
			self.total_cost = self.product_qty * self.cost

	@api.onchange('product_qty')
	def onchange_qty(self):
		if self.cost:
			self.total_cost = self.product_qty * self.cost

class BillofMaterial(models.Model): 
	_inherit = 'mrp.bom'

	total_cost = fields.Float(string="Total Cost")
	resource_cost = fields.Float(string="Total Resource Cost")
	resource_tree = fields.One2many('mrp.resource.cost','resource_cost_tree')

	@api.onchange('bom_line_ids')
	def onchange_product(self):
		total_cost = 0
		if self.bom_line_ids:
			for x in self.bom_line_ids:
				if x.total_cost:
					total_cost = total_cost + x.total_cost

		self.total_cost = total_cost

	@api.onchange('resource_tree')
	def onchange_resource(self):
		total_cost = 0
		if self.resource_tree:
			for x in self.resource_tree:
				if x.total_costed:
					total_cost = total_cost + x.total_costed

		self.resource_cost = total_cost

class ResourcesCost(models.Model):
	_name = 'mrp.resource.cost'
	_rec_name =  'subprocess'

	cost = fields.Float(string="cost")
	total_costed = fields.Float(string="Total")
	time = fields.Float(string="Time")

	sequence = fields.Char(string="Sequence")

	workcenter = fields.Many2one('mrp.workcenter', string="Workcenter")
	resource_cost_tree = fields.Many2one('mrp.bom')
	subprocess = fields.Many2one('mrp.sub.process',string="Subprocess")

	decription = fields.Text(string="Description")

	@api.onchange('subprocess')
	def onchange_process(self):
		if self.subprocess:
			current_prod = self.env['mrp.sub.process'].search([('id','=',self.subprocess.id)])
			self.workcenter = current_prod.workcenter

	@api.onchange('time')
	def onchange_time(self):
		if self.time:
			self.total_costed = self.time * self.cost

	@api.onchange('cost')
	def onchange_cost(self):
		if self.cost:
			self.total_costed = self.time * self.cost

class SubProcess(models.Model):
	_name = 'mrp.sub.process'
	_rec_name =  'name'

	name = fields.Char(string="Name")
	workcenter = fields.Many2one('mrp.workcenter',string="Workcenter")