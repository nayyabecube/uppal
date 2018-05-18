# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError



class MOExtension(models.Model):
	_inherit = 'mrp.production'

	@api.multi
	def create_wo(self):
		number = 0
		for operations in self.routing_id.operation_ids:
			number = number + 1
			final_number = str(self.name) + "-WO" + str(number)
			parent = []
			for par in operations.parent_operations:
				opts = self.env['mrp.routing.workcenter'].search([('sub_process','=',par.id)])
				parent.append(opts.id)
			print parent 

			create_workorders = self.env['ecube.workorders'].create({
						'name': final_number,
						'mo_id': self.id,
						'product_id':self.product_tmpl_id.id,
						'work_center' : operations.workcenter_id.id,
						'operation_name' : operations.id,
						'total_qty' : self.product_qty,	
						})
			create_workorders.parent_operations = parent


