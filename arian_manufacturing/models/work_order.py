# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError



class EcubeWorkOrders(models.Model):
	_name = 'ecube.workorders'


	name = fields.Char()
	mo_id = fields.Many2one('mrp.production',string = "MO Number")
	product_id = fields.Many2one('product.template',string = "Product")
	work_center = fields.Many2one('mrp.workcenter',string = "Work Center")
	operation_name = fields.Many2one("mrp.routing.workcenter",string = "Operation")
	parent_operations = fields.Many2many("mrp.routing.workcenter",string = "Parent Operation")
	total_qty = fields.Integer(string = "Total Quantity")
	received_qty = fields.Integer(string = "Received Quantity")
	remaining_qty = fields.Integer(string = "Remaining Quantity")
	doc_type = fields.Selection([('receiving', 'Receiving'), ('lotting', 'Lotting'),('lot/rec', 'Lotting/Receiving')], string='Document Type')
	wo_receiving = fields.One2many('wo.receiving','workorder_id')
	wo_lotting = fields.One2many('wo.lotting','workorder_id')
	stages = fields.Selection([
		('draft', 'Draft'),
		('progress', 'In Progress'),
		('done', 'Done'),
	], default='draft')


	@api.multi
	def lot_issue(self):
		return {'name': 'Lot Issuing',
				'domain': [],
				'res_model': 'lot.issue',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'view_type': 'form',
				'context': {'default_work_id':self.id},
				'target': 'new', }



	@api.multi
	def lot_rec(self):
		return {'name': 'Lot Receiving',
				'domain': [],
				'res_model': 'lot.receive',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'view_type': 'form',
				'context': {'default_work_id':self.id},
				'target': 'new', }




class WorkOrdersReceiving(models.Model):
	_name = 'wo.receiving'


	lot_no = fields.Many2one('manufacturing.lots',string = "Lot No")
	lot_total_qty = fields.Integer(string = "Lot Total Qty")
	lot_available_qty = fields.Integer(string = "Lot Available Qty")
	qty_received = fields.Integer(string = "Qty Received")
	qty_remaining = fields.Integer(string = "Qty Remaining")
	workorder_id = fields.Many2one('ecube.workorders')

class WorkOrdersLotting(models.Model):
	_name = 'wo.lotting'


	available_lot = fields.Many2one('manufacturing.lots',string = "Available Lot")
	available_qty = fields.Integer(string = "Available Qty")
	qty = fields.Integer(string = "New Lot Qty")
	workorder_id = fields.Many2one('ecube.workorders')


class OperationsExtension(models.Model):
	_inherit = 'mrp.routing.workcenter'

	parent_operations = fields.Many2many('mrp.sub.process')
	sub_process = fields.Many2one('mrp.sub.process')



class LotIssuing(models.Model):
	_name = 'lot.issue'

	operation = fields.Many2many("mrp.routing.workcenter",string = "Operation")
	work_id = fields.Many2one("ecube.workorders")
	issue_id = fields.One2many('lot.issue.tree','issue_tree')





	@api.multi
	def generate(self):
		if self.operation != self.work_id.parent_operations:
			raise  ValidationError('Select')
		if self.issue_id:
			self.issue_id.unlink()

		records = []
		for x in self.operation:
			rec = self.env['manufacturing.lots'].search([('operation_name','=',x.id)])
			if rec:
				for y in rec:
					records.append(y)


		for z in records:
			nonactiverec = self.env['lot.issue.tree']
			create_rec = nonactiverec.create({
				'lot': z.id,
				'mo_id': z.mo_id.id,
				'lot_qty': z.lot_qty,
				'issue_qty': z.issued_qty,
				'issue_tree': self.id,
				})

		return {
		"type": "ir.actions.do_nothing",
		}
		

	@api.multi
	def done(self):
		if self.issue_id:
			issue_list = []
			count = 0
			for x in self.issue_id:
				count = count + 1
				issue_list.append(x.issue_qty)
			if count == 2:
				if issue_list[0] != issue_list[1]:
					raise  ValidationError('Select')
				else:
					for y in self.issue_id:
						self.assign_list(y.lot.id,y.lot_qty,y.issue_qty)

			else:
				for y in self.issue_id:
					self.assign_list(y.lot.id,y.lot_qty,y.issue_qty)

			self.create_lot()



	def assign_list(self,idz,qty,issue):
		rec = []
		rec.append({
			'available_lot':idz,
			'available_qty':qty,
			'qty':issue,
			'workorder_id':self.work_id.id,
			})

		self.work_id.wo_lotting = rec

	def create_lot(self):
		value = 0
		for i in self.issue_id:
			value = i.issue_qty
		lot_creation = self.env['manufacturing.lots']
		create_rec = lot_creation.create({
			'mo_id': self.work_id.mo_id.id,
			'operation_name': self.work_id.operation_name.id,
			'lot_qty':value,
			})

		for w in self.issue_id:
			a = create_rec.tree_id.create({
					'lot_id': w.lot.id,
					'lot_tree': create_rec.id,
				})






class LotIssuingTree(models.Model):
	_name = 'lot.issue.tree'


	lot = fields.Many2one('manufacturing.lots',string="Lot")
	mo_id = fields.Many2one('mrp.production',string="Mo Id")
	lot_qty = fields.Float(string="Lot Qty")
	issue_qty = fields.Float(string="Isuued Qty")
	issue_tree = fields.Many2one('lot.issue')






class LotReceiving(models.Model):
	_name = 'lot.receive'

	operation = fields.Many2many("mrp.routing.workcenter",string = "Operation")
	work_id = fields.Many2one("ecube.workorders")
	receive_id = fields.One2many('lot.receive.tree','receive_tree')





	@api.multi
	def generate(self):
		if self.receive_id:
			self.receive_id.unlink()

		records = []
		for x in self.operation:
			rec = self.env['manufacturing.lots'].search([('operation_name','=',x.id)])
			if rec:
				for y in rec:
					records.append(y)


		for z in records:
			nonactiverec = self.env['lot.receive.tree']
			create_rec = nonactiverec.create({
				'lot': z.id,
				'mo_id': z.mo_id.id,
				'lot_qty': z.lot_qty,
				'to_receive': z.to_receive,
				'received': z.received,
				'remaining_qty': z.remaining_qty,
				'receive_tree': self.id,
				})

		return {
		"type": "ir.actions.do_nothing",
		}


	@api.multi
	def done(self):
		if self.receive_id:
			for x in self.receive_id:
				rec = []
				rec.append({
					'lot_no':x.lot.id,
					'lot_total_qty':x.lot_qty,
					'lot_available_qty':x.to_receive,
					'qty_received':x.received,
					'qty_remaining':x.remaining_qty,
					'workorder_id':self.work_id.id,
					})
				self.work_id.wo_receiving = rec
				x.lot.received = x.received
				x.lot.remaining_qty = x.remaining_qty
				x.lot.to_receive = x.to_receive
				x.lot.get_values()
				x.lot.change_stages()






class LotReceivingTree(models.Model):
	_name = 'lot.receive.tree'


	lot = fields.Many2one('manufacturing.lots',string="Lot")
	mo_id = fields.Many2one('mrp.production',string="Mo Id")
	lot_qty = fields.Float(string="Lot Qty")
	to_receive = fields.Float(string="Lot Available Qty")
	received = fields.Float(string="Qty Received")
	remaining_qty = fields.Float(string="Qty Remaining")
	receive_tree = fields.Many2one('lot.receive')


# 	name = fields.Char()
# 	mo_id = fields.Many2one('mrp.production')
# 	wo_id = fields.Many2one('mrp.workorder')



# class account_bank_extension(models.Model):
# 	_inherit = 'account.bank.statement'


# 	account_id = fields.Many2one('account.account', string = "Account Head")
# 	state = fields.Selection([('open', 'New'), ('in_progress', 'In Progress'),('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open')
# 	current_balance = fields.Float(string = "Current Balance", compute = "compute_balance")

# 	@api.onchange('account_id')
# 	def compute_name(self):
# 		if self.account_id:
# 			self.name = str(self.account_id.code) + " - " + str(self.account_id.name)

# 	@api.one
# 	def compute_balance(self):
# 		debit = 0
# 		credit = 0
# 		entries = self.env['account.move.line'].search([('account_id','=',self.account_id.id)])
# 		for amounts in entries:
# 			debit = debit + amounts.debit
# 			credit = credit + amounts.credit
# 		self.current_balance = debit - credit


# 	@api.multi
# 	def in_progress(self):
# 		self.state = "in_progress"

# 	@api.multi
# 	def validate_entries(self):
# 		self.post()
# 		self.state = "confirm"
# 		for x in self.line_ids:
# 			x.journal_entry_id.post()
			
# 	@api.multi
# 	def reset_progress(self):
# 		self.state = "in_progress"
# 		for lines in self.line_ids:
# 			lines.journal_entry_id.button_cancel()


# 	@api.multi
# 	def post(self):
# 		journal_entries = self.env['account.move']
# 		journal_entries_lines = self.env['account.move.line']
# 		for x in self.line_ids:
# 			x.journal_entry_id.unlink()
# 			if not x.journal_entry_id:
# 				create_journal = journal_entries.create({
# 					'journal_id': self.journal_id.id,
# 					'date':x.date,
# 					'ref' : self.name,
# 					})
# 				if x.amount > 0:
# 					debit_account = self.account_id.id
# 					credit_account = x.account_id.id
# 				if x.amount < 0:
# 					debit_account = x.account_id.id
# 					credit_account = self.account_id.id 
# 				debit = journal_entries_lines.create({
# 					'account_id':debit_account,
# 					'partner_id':x.partner_id.id,
# 					'name':x.name,
# 					'debit':abs(x.amount),
# 					'credit':0,
# 					'move_id':create_journal.id,
# 					})

# 				credit = journal_entries_lines.create({
# 					'account_id':credit_account,
# 					'partner_id':x.partner_id.id,
# 					'name':x.name,
# 					'debit':0,
# 					'credit':abs(x.amount),
# 					'move_id':create_journal.id,
# 					})

# 				x.journal_entry_id = create_journal.id






# class account_bank_extension_line(models.Model):
# 	_inherit = 'account.bank.statement.line'


	
# 	journal_entry_id = fields.Many2one('account.move',string="Debit")
# 	bank = fields.Many2one('account.account',string="Credit")
# 	paid = fields.Float(string="Paid")
# 	received = fields.Float(string="Received")
# 	head_wise_id = fields.Many2one('head.wise.entries')



# 	@api.multi
# 	def post(self):
# 		# head_wise = self.env['head.wise.entries'].search([('line_id','=',self.id)])
# 		if self.head_wise_id:
# 			return {
# 					'type': 'ir.actions.act_window',
# 	                'view_type': 'form',
# 	                'name': 'Head Wise',
# 	                'view_mode': 'form',
# 	                'res_model': 'head.wise.entries',
# 	                'target': 'new',
# 	                'res_id': self.head_wise_id.id,
					
# 					}
# 		else:
# 			ctx = dict(
# 	            default_line_id= self.id,
# 	        )
# 			return {
# 			'type': 'ir.actions.act_window',
# 			'name': 'Head Wise',
# 			'res_model': 'head.wise.entries',
# 			'view_type': 'form',
# 			'view_mode': 'form',
# 			'target' : 'new',
# 			'context':ctx
# 			}

# 	@api.onchange('paid')
# 	def getamount(self):
# 		if self.paid:
# 			self.received = 0
# 			self.amount = self.paid * -1

# 	@api.onchange('received')
# 	def getamountrec(self):
# 		if self.received:
# 			self.paid = 0
# 			self.amount = self.received 


# 	@api.multi
# 	def unlink(self):
# 		self.journal_entry_id.unlink()
# 		super(account_bank_extension_line, self).unlink()


	


# class account_move_extend(models.Model):
# 	_inherit = 'account.move'

# 	@api.multi
# 	def assert_balanced(self):
# 		if not self.ids:
# 			return True
# 		prec = self.env['decimal.precision'].precision_get('Account')

# 		self._cr.execute("""\
# 			SELECT      move_id
# 			FROM        account_move_line
# 			WHERE       move_id in %s
# 			GROUP BY    move_id
# 			HAVING      abs(sum(debit) - sum(credit)) > %s
# 			""", (tuple(self.ids), 10 ** (-max(5, prec))))
# 		# if len(self._cr.fetchall()) != 0:
# 		#     raise UserError(_("Cannot create unbalanced journal entry."))
# 		return True


# class HeadWiseEntries(models.Model):
# 	_name = 'head.wise.entries'

# 	name = fields.Char()
# 	line_id = fields.Integer()
# 	head_wise_tree = fields.One2many('head.wise.lines','head_wise_id')


# 	def update_cashbook(self):
# 		paid = 0
# 		received = 0
# 		for lines in self.head_wise_tree:
# 			paid = paid + lines.paid
# 			received = received + lines.received

# 		cash_lines = self.env['account.bank.statement.line'].search([('id','=',self.line_id)])
# 		cash_lines.paid = paid
# 		cash_lines.received = received
# 		cash_lines.head_wise_id = self.id



# class HeadWiseEntriesLines(models.Model):
# 	_name = 'head.wise.lines'


# 	account_id = fields.Many2one('account.account', string = "Account Head")
# 	paid = fields.Float(string="Paid")
# 	received = fields.Float(string="Received")
# 	head_wise_id = fields.Many2one('head.wise.entries')

	




# 	@api.onchange('paid')
# 	def getamount(self):
# 		if self.paid:
# 			self.received = 0
# 			self.amount = self.paid * -1

# 	@api.onchange('received')
# 	def getamountrec(self):
# 		if self.received:
# 			self.paid = 0
# 			self.amount = self.received 

	


	


