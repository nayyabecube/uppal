# -*- coding: utf-8 -*-
from openerp import models, fields, api
from odoo.exceptions import Warning, ValidationError



class account_bank_extension(models.Model):
	_inherit = 'account.bank.statement'

	@api.multi
	def post(self):
		value = 0
		rec = self.env['account.journal'].search([('id','=',self.journal_id.id)])
		value = rec.default_debit_account_id.id
		journal_entries = self.env['account.move'].search([])
		journal_entries_lines = self.env['account.move.line'].search([])
		for x in self.line_ids:
			if x.account and x.e_check == False:
				create_journal = journal_entries.create({
					'journal_id': self.journal_id.id,
					'date':self.date,
					'ref' : self.name,
					})

				if x.received > 0.00 and x.paid == 0.00:

					b = journal_entries_lines.create({
						'account_id':x.account.id,
						'partner_id':x.partner_id.id,
						'name':x.name,
						'debit':x.received,
						'credit':0.0,
						'move_id':create_journal.id,
						})

					c = journal_entries_lines.create({
						'account_id':value,
						'partner_id':x.partner_id.id,
						'name':x.name,
						'debit':0.0,
						'credit':x.received,
						'move_id':create_journal.id,
						})

					x.ecube_journal = create_journal.id
					x.e_check = True

				if x.paid > 0.00 and x.received == 0.00:

					b = journal_entries_lines.create({
						'account_id':x.account.id,
						'partner_id':x.partner_id.id,
						'name':x.name,
						'debit':0.0,
						'credit':x.paid,
						'move_id':create_journal.id,
						})

					c = journal_entries_lines.create({
						'account_id':value,
						'partner_id':x.partner_id.id,
						'name':x.name,
						'debit':x.paid,
						'credit':0.0,
						'move_id':create_journal.id,
						})

					x.ecube_journal = create_journal.id
					x.e_check = True


	@api.model
	def create(self, vals):
		rec = self.env['account.bank.statement'].search([])
		for x in rec:
			for y in x.line_ids:
				if y.e_check == False:
					raise  ValidationError('Post Pending Enteries In Previous Cash Books')

		new_record = super(account_bank_extension, self).create(vals)
		return new_record



class account_bank_extension_line(models.Model):
	_inherit = 'account.bank.statement.line'


	account = fields.Many2one('account.account',string="Account")
	ecube_journal = fields.Many2one('account.move',string="Journal")
	e_check = fields.Boolean()
	paid = fields.Float(string='Paid')
	received = fields.Float(string='Received')
	
	@api.onchange('paid')
	def paid_amount(self):
		negative=-1
		if self.paid:
			self.amount= self.paid * negative
			self.received=0

	@api.onchange('received')
	def received_amount(self):
		if self.received:
			self.amount= self.received
			self.paid=0

	@api.multi
	def unlink(self):
		if self.e_check == True:
			raise  ValidationError('Post Pending')

		super(account_bank_extension_line, self).unlink()

		return True


# class account_move_line(models.Model):
# 	_inherit = 'account.move.line'

# 	voucher_no = fields.Char(string="Voucher No.")
# 	payess_name = fields.Many2one('res.partner',string="Payees Name")

class account_move_extend(models.Model):
	_inherit = 'account.move'

	@api.multi
	def assert_balanced(self):
		if not self.ids:
			return True
		prec = self.env['decimal.precision'].precision_get('Account')

		self._cr.execute("""\
			SELECT      move_id
			FROM        account_move_line
			WHERE       move_id in %s
			GROUP BY    move_id
			HAVING      abs(sum(debit) - sum(credit)) > %s
			""", (tuple(self.ids), 10 ** (-max(5, prec))))
		# if len(self._cr.fetchall()) != 0:
		#     raise UserError(_("Cannot create unbalanced journal entry."))
		return True

