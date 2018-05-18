# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError



class ManufacturingLots(models.Model):
	_name = 'manufacturing.lots'


	name = fields.Char(readonly=True)
	mo_id = fields.Many2one('mrp.production')
	wo_id = fields.Many2one('mrp.workorder')
	lot_qty = fields.Float(string = "Lot Qty")
	received = fields.Float(string = "Received")
	to_receive = fields.Float(string = "Qty to Receive")
	issued_qty = fields.Float(string = "Issued Qty")
	remaining_qty = fields.Float(string = "Remaining Qty")
	operation_name = fields.Many2one("mrp.routing.workcenter",string = "Operation")
	tree_id = fields.One2many('manufacturing.lots.tree','lot_tree')
	stages = fields.Selection([
		('lot_create', 'Lot Created'),
		('partial_rec', 'Partially Received'),
		('receive', 'Received'),
		('done', 'Done'),
	], default='lot_create')
	



	def get_values(self):
		if self.lot_qty:
			if self.received > self.lot_qty:
				raise  ValidationError('Cannot Receive More Qty Than Lot Qty')
			else:
				self.to_receive = self.lot_qty - self.received
			if self.issued_qty:
				if self.issued_qty > self.received:
					raise  ValidationError('Cannot Issue More Qty Than Receive Qty')
				else:
					self.remaining_qty = self.received - self.issued_qty


					
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('lot.seq')
		new_record = super(ManufacturingLots, self).create(vals)

		return new_record




	def change_stages(self):
		if self.received:
			if self.to_receive > 0 and self.to_receive < self.lot_qty:
				self.stages = 'partial_rec'
			if self.to_receive == 0:
				self.stages = 'receive'
		if self.issued_qty:
			if self.remaining_qty == 0:
				self.stages = 'done'


class ManufacturingLotsTree(models.Model):
	_name = 'manufacturing.lots.tree'


	lot_id = fields.Many2one('manufacturing.lots',string="Pervious Lots")
	lot_tree = fields.Many2one('manufacturing.lots')











# class ManufacturingLots(models.Model):
# 	_name = 'manufacturing.lots'


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

	


	


