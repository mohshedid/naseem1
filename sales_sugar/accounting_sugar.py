# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
import datetime



class FundsFlow(models.Model): 
	_name 		 = 'funds.flow' 
	_description = 'Funds Flow'
	_rec_name = 'date'


	date = fields.Date(required=True, default=fields.Date.context_today, string = "Work Date")
	total_jv = fields.Float(string = "Total JV", compute = "get_totals", store = True)
	total_receipts = fields.Float(string = "Total Receipts", compute = "get_totals", store = True)
	total_payments = fields.Float(string = "Total Payments", compute = "get_totals", store = True)
	
	customer = fields.Many2one('res.partner',string = "From")
	supplier = fields.Many2one('res.partner',string = "Payment To")
	party = fields.Many2one('res.partner',string = "Party")

	check = fields.Boolean(compute = "check_box", default = True)
	parties = fields.Many2many('res.partner')



	fund_lines = fields.One2many('funds.flow.tree','funds_flow_id')
	fund_lines_jv = fields.One2many('funds.flow.tree','funds_flow_jv')



	@api.one
	@api.depends('fund_lines_jv','fund_lines')
	def get_totals(self):
		total_jv = 0
		for x in self.fund_lines_jv:
			total_jv = total_jv + x.amount
		self.total_jv = total_jv

		total_receipts = 0
		total_payments = 0
		for y in self.fund_lines:
			if y.type_transaction == "br":
				total_receipts = total_receipts +y.amount
			if y.type_transaction == "bp":
				total_payments = total_payments + y.amount
		self.total_receipts = total_receipts
		self.total_payments = total_payments



	def check_box(self):
		self.check = True


	@api.one
	@api.constrains('date')
	def single_date(self):

		dates = self.env['funds.flow'].search([('date','=',self.date),('id','!=',self.id)])
		if dates:
			raise ValidationError('Date Already Exists')


	@api.onchange('date')
	def change_date(self):
		for x in self.fund_lines:
			x.date = self.date
		for x in self.fund_lines_jv:
			x.date = self.date



	@api.onchange('fund_lines','fund_lines_jv')
	def get_balances(self):
		if self.fund_lines or self.fund_lines_jv:

			self.check = False


			parties = []
			for x in self.fund_lines:
				if not x.id :
					if x.party.id not in parties:
						parties.append(x.party.id)
			for y in self.fund_lines_jv:
				if not y.id:
					if y.customer.id not in parties:
						parties.append(y.customer.id)

					if y.supplier.id not in parties:
						parties.append(y.supplier.id)

			parties_field = []
			for x in self.parties:
				parties_field.append(x.id)

			for x in parties:
				if x not in parties_field:
					parties_field.append(x)

			self.parties = parties_field



			
			for x in self.parties:
				total = 0
				for y in self.fund_lines:
					if not y.id:
						if y.party.id == x.id:
							if y.type_transaction == "br":
								total = total + y.amount
							if y.type_transaction == "bp":
								total = total - y.amount
				for y in self.fund_lines_jv:
					if not y.id:
						if y.customer.id == x.id:
							total = total + y.amount
						if y.supplier.id == x.id:
							total = total - y.amount



			summary = self.env['summary.entry'].search([('customer','=',x.id)])
			summary.write({'temporary':total})





class FundsFLowTree(models.Model): 
	_name 		 = 'funds.flow.tree'
	_description = 'Funds Flow'
	# _rec_name = 'date'

	customer = fields.Many2one('res.partner',string = "From" )
	party = fields.Many2one('res.partner',string = "Party")
	amount = fields.Float()
	bank = fields.Many2one('account.account')
	remarks = fields.Char()
	supplier = fields.Many2one('res.partner',string = "Payment To" ,domain="[('id', '!=',customer )]")   
																				
	banks_pakistan = fields.Many2one('banks.pakistan',string = "Party Bank")
	bank_code = fields.Char(string = "Code")

	supplier_bank = fields.Many2one('banks.pakistan',string = "Supplier Bank")
	supplier_bank_code = fields.Char(string = "Code")
	type_transaction = fields.Selection([
		
		('br', 'Receipt'),
		('bp', 'Payment'),
		('jv', 'Journal Voucher'),
		],string = "Voucher Type",default = "br")
	date = fields.Date(required=True,string = "Entry Date")
	date_clearance = fields.Date(string ="Clearance Date")
	date_confirmation = fields.Date(string="Confirmation Date")
	stages = fields.Selection([
		('entry', 'Entry Level'),
		('clearing', 'Clearing'),
		('confirmation', 'Confirmation'),
		],string = "Stages", default = 'entry')
	j_entry_id = fields.Many2one('account.move')
	cash_id = fields.Many2one('account.bank.statement')

	entry_level = fields.Float(string = "Entry Level")
	clearance_level = fields.Float(string = "Clearance Level")
	virtual_balance = fields.Float(string = "Virtual Balance")
	actual_balance = fields.Float(string = "Actual Balance")

	entry_level_ch = fields.Char(string = "Entry Level")
	clearance_ch = fields.Char(string = "Clearance Level")
	virtual_ch = fields.Char(string = "Virtual Balance")
	actual_ch = fields.Char(string = "Actual Balance")


	funds_flow_id = fields.Many2one('funds.flow')
	funds_flow_jv = fields.Many2one('funds.flow')


	@api.model
	def create(self, vals):
		new_record = super(FundsFLowTree, self).create(vals)
		if new_record.funds_flow_id:
			if new_record.bank.name == "Cash":
				cash_book = self.env['account.bank.statement'].search([('state','=',"open")])
				if not cash_book:
					raise ValidationError('No Cash Book is open, you cannot create Cash related entries')
				else:
					new_record.cash_id = cash_book.id

			
			summary = self.env['summary.entry'].search([('customer','=',new_record.party.id)])
			if new_record.type_transaction == "br":
				for x in summary:
					x.receivable = x.receivable + new_record.amount

			elif new_record.type_transaction == "bp":
				for x in summary:
					x.payable = x.payable + new_record.amount
			summary.net = summary.receivable - summary.payable

				
		elif new_record.funds_flow_jv:


			summary = self.env['summary.entry'].search([('customer','=',new_record.customer.id)])
			for x in summary:
				x.receivable = x.receivable + new_record.amount
			summary.net = summary.receivable - summary.payable



			summary = self.env['summary.entry'].search([('customer','=',new_record.supplier.id)])
			for x in summary:
				x.payable = x.payable + new_record.amount
			summary.net = summary.receivable - summary.payable
		

		journal_entries_lines = self.env['account.move.line'].search([])
		journal_entries = self.env['account.move'].search([])




		if new_record.type_transaction == "br":
			journal_id = self.env['account.journal'].search([('code','=',"BR")])

			create_journal_entry = journal_entries.create({
					'journal_id': journal_id.id,
					'date':new_record.date,
					'funds_flow_id':new_record.id,
					})
			create_debit = journal_entries_lines.create({
				'account_id':new_record.bank.id,
				'partner_id':new_record.party.id,
				'name':"Received" + " "+ str(new_record.amount) + "  " + "From" + "  "+ str(new_record.banks_pakistan.name)+str(new_record.bank_code) + " " +str(new_record.party.name)+  " in " + str(new_record.bank.code)+ " " +str(new_record.bank.name)+  " "  + str(new_record.remarks if new_record.remarks else ""), 
				'debit':new_record.amount,
				'move_id':create_journal_entry.id
				})
			party_ledger = self.env['account.account'].search([('name','=',"Party Ledgers")])
			create_credit = journal_entries_lines.create({
				'account_id':party_ledger.id,
				'partner_id':new_record.party.id,
				'name':"Received" + " "+ str(new_record.amount) + "  " + "From" + "  "+ str(new_record.banks_pakistan.name)+str(new_record.bank_code) + " " +str(new_record.party.name)+  " in " + str(new_record.bank.code)+ " " +str(new_record.bank.name)+  " "  + str(new_record.remarks if new_record.remarks else ""),   
				'credit':new_record.amount,
				'move_id':create_journal_entry.id
				})
			# new_record.j_entry_id = create_journal_entry.id

		if new_record.type_transaction == "bp":
			journal_id = self.env['account.journal'].search([('code','=',"BP")])
			create_journal_entry = journal_entries.create({
					'journal_id': journal_id.id,
					'date':new_record.date,
					'funds_flow_id':new_record.id,
					})
			party_ledger = self.env['account.account'].search([('name','=',"Party Ledgers")])

			create_debit = journal_entries_lines.create({
				'account_id':party_ledger.id,
				'partner_id':new_record.party.id,
				'name':"Paid" + " "+ str(new_record.amount) + "  " + "To" + "  "+str(new_record.party.name) + " in " + str(new_record.banks_pakistan.name) + " " + str(new_record.bank_code) + " " +"From "+ str(new_record.bank.code)+ " " +str(new_record.bank.name)+ " "+ str(new_record.remarks if new_record.remarks else ""), 
				'debit':new_record.amount,
				'move_id':create_journal_entry.id
				})
			create_credit = journal_entries_lines.create({
				'account_id':new_record.bank.id,
				'partner_id':new_record.party.id,
				'name':"Paid" + " "+ str(new_record.amount) + "  " + "To" + "  "+str(new_record.party.name) + " in " + str(new_record.banks_pakistan.name) + " " + str(new_record.bank_code) + " " +"From "+ str(new_record.bank.code)+ " " +str(new_record.bank.name)+ " "+ str(new_record.remarks if new_record.remarks else ""), 
				'credit':new_record.amount,
				'move_id':create_journal_entry.id
				})

			# new_record.j_entry_id = create_journal_entry.id


		if new_record.type_transaction == "jv":
			journal_id = self.env['account.journal'].search([('code','=',"JV")])
			create_journal_entry = journal_entries.create({
						'journal_id': journal_id.id,
						'date':new_record.date,
						'funds_flow_id':new_record.id,
						})
			party_ledger = self.env['account.account'].search([('name','=',"Party Ledgers")])

			create_debit = journal_entries_lines.create({
				'account_id':party_ledger.id,
				'partner_id':new_record.supplier.id,
				'name':"Payment from" + " "+ str(new_record.customer.name) + "  " + str(new_record.banks_pakistan.name)+ str(new_record.bank_code)+" "+"To" + "  "+str(new_record.supplier.name) + " in " + str(new_record.supplier_bank.name) + " " + str(new_record.supplier_bank_code) + " " + str(new_record.remarks if new_record.remarks else ""), 
				'debit':new_record.amount,
				'move_id':create_journal_entry.id
				})
			create_credit = journal_entries_lines.create({
				'account_id':party_ledger.id,
				'partner_id':new_record.customer.id,
				'name':"Payment from" + " "+ str(new_record.customer.name) + "  " + str(new_record.banks_pakistan.name)+ str(new_record.bank_code)+" "+"To" + "  "+str(new_record.supplier.name) + " in " + str(new_record.supplier_bank.name) + " " + str(new_record.supplier_bank_code) + " " + str(new_record.remarks if new_record.remarks else ""), 
				'credit':new_record.amount,
				'move_id':create_journal_entry.id
				})

			# new_record.j_entry_id = create_journal_entry.id




		return new_record


	@api.multi
	def write(self, vals):


		if self.stages == "entry":

			if self.bank.name == "Cash":

				print self.cash_id.id
				cash_book = self.env['account.bank.statement'].search([('id','=',self.cash_id.id)])
				if cash_book:
					if cash_book.state != "open":
						raise ValidationError('You cannot edit the validated Cash Book Entry')
					else:
						if self.type_transaction == "br":
							cash_book.funds_flow = cash_book.funds_flow - self.amount
						if self.type_transaction == "bp":
							cash_book.funds_flow = cash_book.funds_flow + self.amount

			if self.type_transaction == "jv":
				summary_to = self.env['summary.entry'].search([('customer','=',self.supplier.id)])
				summary_from = self.env['summary.entry'].search([('customer','=',self.customer.id)])
				for x in summary_to:
					x.payable = x.payable - self.amount
				for x in summary_from:
					x.receivable = x.receivable - self.amount
					x.net = x.receivable - x.payable


			summary = self.env['summary.entry'].search([('customer','=',self.party.id)])

			if self.type_transaction == "br":
				for x in summary:
					x.receivable = x.receivable - self.amount
					x.net = x.receivable - x.payable
		

			if self.type_transaction == "bp":
				for x in summary:
					x.payable = x.payable - self.amount
					x.net = x.receivable - x.payable

		if self.stages == "clearing":

			if self.type_transaction == "jv":
				summary_to = self.env['summary.clearance'].search([('customer','=',self.supplier.id)])
				summary_from = self.env['summary.clearance'].search([('customer','=',self.customer.id)])
				for x in summary_to:
					x.payable = x.payable - self.amount
					x.net = x.receivable - x.payable
				for x in summary_from:
					x.receivable = x.receivable - self.amount
					x.net = x.receivable - x.payable


			summary = self.env['summary.clearance'].search([('customer','=',self.party.id)])

			if self.type_transaction == "br":
				for x in summary:
					x.receivable = x.receivable - self.amount
					x.net = x.receivable - x.payable
		

			if self.type_transaction == "bp":
				for x in summary:
					x.payable = x.payable - self.amount
					x.net = x.receivable - x.payable




	
		super(FundsFLowTree, self).write(vals)

		if self.stages == "entry":

			if self.bank.name == "Cash":
				cash_book = self.env['account.bank.statement'].search([('id','=',self.cash_id.id)])
				if cash_book:
					if self.type_transaction == "br":
						cash_book.funds_flow = cash_book.funds_flow + self.amount
					if self.type_transaction == "bp":
						cash_book.funds_flow = cash_book.funds_flow - self.amount
				else:
					cash_book = self.env['account.bank.statement'].search([('state','=',"open")])
					if not cash_book:
						raise ValidationError('No Cash Book is open, you cannot create Cash related entries')
					else:
						self.cash_id = cash_book.id

			summary = self.env['summary.entry'].search([('customer','=',self.party.id)])

			if self.type_transaction == "br":
				for x in summary:
					x.receivable = x.receivable + self.amount
					x.net = x.receivable - x.payable
			if self.type_transaction == "bp":
				for x in summary:
					x.payable = x.payable + self.amount
					x.net = x.receivable - x.payable

			if self.type_transaction == "jv":
				summary_to = self.env['summary.entry'].search([('customer','=',self.supplier.id)])
				summary_from = self.env['summary.entry'].search([('customer','=',self.customer.id)])
				for x in summary_to:
					x.payable = x.payable + self.amount
					x.net = x.receivable - x.payable
				for x in summary_from:
					x.receivable = x.receivable + self.amount
					x.net = x.receivable - x.payable

		if self.stages == "clearing":
			summary = self.env['summary.clearance'].search([('customer','=',self.party.id)])

			if self.type_transaction == "br":
				for x in summary:
					x.receivable = x.receivable + self.amount
					x.net = x.receivable - x.payable
			if self.type_transaction == "bp":
				for x in summary:
					x.payable = x.payable + self.amount
					x.net = x.receivable - x.payable

			if self.type_transaction == "jv":
				summary_to = self.env['summary.clearance'].search([('customer','=',self.supplier.id)])
				summary_from = self.env['summary.clearance'].search([('customer','=',self.customer.id)])
				for x in summary_to:
					x.payable = x.payable + self.amount
					x.net = x.receivable - x.payable
				for x in summary_from:
					x.receivable = x.receivable + self.amount
					x.net = x.receivable - x.payable




		journal_entries = self.env['account.move'].search([('funds_flow_id','=',self.id)])
		if self.type_transaction == "br":

			for y in journal_entries.line_ids:
				if y.debit > 0 and y.credit ==0:
					y.account_id = self.bank.id
					y.partner_id = self.party.id
					y.name = "Received" + " "+ str(self.amount) + "  " + "From" + "  "+str(self.banks_pakistan.name)+str(self.bank_code)+" "+str(self.party.name)+ " in " + str(self.bank.code) +str(self.bank.name)+  " "  + str(self.remarks if self.remarks else "")
					y.debit = self.amount
				else:
					y.partner_id = self.party.id
					y.name = "Received" + " "+ str(self.amount) + "  " + "From" + "  "+str(self.banks_pakistan.name)+str(self.bank_code)+" "+str(self.party.name)+ " in " + str(self.bank.code) +str(self.bank.name)+  " "  + str(self.remarks if self.remarks else "")
					y.credit = self.amount


		elif self.type_transaction == "bp":
			for y in journal_entries.line_ids:
				if y.credit > 0 and y.debit ==0:
					y.account_id = self.bank.id
					y.partner_id = self.party.id
					y.name = "Paid" + " "+ str(self.amount) + "  " + "To" + "  "+str(self.party.name) + " in " + str(self.banks_pakistan.name) + " " + str(self.bank_code) + " " +"From "+ str(self.bank.code)+ " " +str(self.bank.name)+ " "+ str(self.remarks if self.remarks else ""),
					y.credit = self.amount
					 
				else:
					y.partner_id = self.party.id
					y.name = "Paid" + " "+ str(self.amount) + "  " + "To" + "  "+str(self.party.name) + " in " + str(self.banks_pakistan.name) + " " + str(self.bank_code) + " " +"From "+ str(self.bank.code)+ " " +str(self.bank.name)+ " "+ str(self.remarks if self.remarks else ""),
					y.debit = self.amount

		else: 
			for y in journal_entries.line_ids:

				if y.credit > 0 and y.debit ==0:
					y.partner_id = self.customer.id
					y.name = "Payment from" + " "+ str(self.customer.name) + "  " + str(self.banks_pakistan.name)+ str(self.bank_code)+" "+"To" + "  "+str(self.supplier.name) + " in " + str(self.supplier_bank.name) + " " + str(self.supplier_bank_code) + " " + str(self.remarks if self.remarks else ""), 
					y.credit = self.amount
					 
				else:
					y.partner_id = self.supplier.id
					y.name = "Payment from" + " "+ str(self.customer.name) + "  " + str(self.banks_pakistan.name)+ str(self.bank_code)+" "+"To" + "  "+str(self.supplier.name) + " in " + str(self.supplier_bank.name) + " " + str(self.supplier_bank_code) + " " + str(self.remarks if self.remarks else ""), 
					y.debit = self.amount



		
		return True
	
	

	@api.multi
	def unlink(self):

		if self.bank.name == "Cash":
			cash_book = self.env['account.bank.statement'].search([('id','=',self.cash_id.id)])
			for x in cash_book:
				if x.state == "validate":
					raise ValidationError('You cannot delete the Cash entry in Validated State')
				else:
					if self.type_transaction == "br":
						x.funds_flow = x.funds_flow - self.amount
					if self.type_transaction == "bp":
						x.funds_flow = x.funds_flow + self.amount

		journal_delete = self.env['account.move'].search([('funds_flow_id','=',self.id)])
		journal_delete.unlink()


		summary = self.env['summary.entry'].search([('customer','=',self.party.id)])

		if self.type_transaction == "br":
			for x in summary:
				x.receivable = x.receivable - self.amount
				x.net = x.receivable - x.payable


		if self.type_transaction == "bp":
			for x in summary:
				x.payable = x.payable - self.amount
				x.net = x.receivable - x.payable


		if self.type_transaction == "jv":
			summary_to = self.env['summary.entry'].search([('customer','=',self.supplier.id)])
			summary_from = self.env['summary.entry'].search([('customer','=',self.customer.id)])
			for x in summary_to:
				x.payable = x.payable - self.amount
				x.net = x.receivable - x.payable
			for x in summary_from:
				x.receivable = x.receivable - self.amount
				x.net = x.receivable - x.payable

		if self.stages != "entry":
			raise ValidationError('You can only delete "Entry Level" records')


		super(FundsFLowTree, self).unlink()



		return True



	@api.multi
	def back_to_entry(self):
		self.stages = "entry"

	@api.multi
	def back_to_clearance(self):


		journal_entry = self.env['account.move'].search([('id','=',self.j_entry_id.id)])
		if journal_entry.state == "post":
			raise ValidationError('First Cancel the Posted Entry')
		else:
			self.stages = "clearing"





	@api.onchange('type_transaction')
	def get_to_from(self):

		if not self.customer:
			self.customer = self.funds_flow_jv.customer 
		if not self.supplier:
			self.supplier = self.funds_flow_jv.supplier
		if not self.party:
			self.party = self.funds_flow_id.party
		

		


	@api.onchange('party','customer','supplier')
	def get_date(self):
		if self.funds_flow_id:
			if self.party:
				date = self.funds_flow_id.date
				self.date = date

				summary = self.env['summary.entry'].search([('customer','=',self.party.id)])
				if self.funds_flow_id.check == True:
					self.entry_level = summary.net
				else:
					self.entry_level = summary.net + summary.temporary

				summary_clearance = self.env['summary.clearance'].search([('customer','=',self.party.id)])
				self.clearance_level = summary_clearance.net
				journal_lines_actual= self.env['account.move.line'].search([('partner_id','=',self.party.id),('move_id.state','=',"posted"),('account_id.name','in',["Account Payable","Account Receivable"])])
				debit = 0
				credit = 0
				for x in journal_lines_actual:
					debit = debit + x.debit
					credit = credit + x.credit
				balance = debit - credit
				self.actual_balance = summary.balance
				self.virtual_balance = self.actual_balance - self.entry_level - self.clearance_level



		if self.funds_flow_jv:
			if self.customer and self.supplier:
				date = self.funds_flow_jv.date
				self.date = date

				self.type_transaction = "jv"
				summary_to = self.env['summary.entry'].search([('customer','=',self.supplier.id)])
				summary_from = self.env['summary.entry'].search([('customer','=',self.customer.id)])
				if self.funds_flow_jv.check == True:
					self.entry_level_ch = str(summary_from.net) + " / " + str(summary_to.net)
				else:
					self.entry_level_ch = str(summary_from.net + summary_from.temporary) + " / " + str(summary_to.net + summary_to.temporary)

				summary_clearance_to = self.env['summary.clearance'].search([('customer','=',self.supplier.id)])
				summary_clearance_from = self.env['summary.clearance'].search([('customer','=',self.customer.id)])
				self.clearance_ch = str(summary_clearance_from.net) + " / " + str(summary_clearance_to.net)


				journal_lines_actual_from= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('move_id.state','=',"posted"),('account_id.name','in',["Account Payable","Account Receivable"])])
				debit = 0
				credit = 0
				for x in journal_lines_actual_from:
					debit = debit + x.debit
					credit = credit + x.credit
				balance_from = debit - credit

				journal_lines_actual_to= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('move_id.state','=',"posted"),('account_id.name','in',["Account Payable","Account Receivable"])])
				
				debit = 0
				credit = 0
				for x in journal_lines_actual_to:
					debit = debit + x.debit
					credit = credit + x.credit
				balance_to = debit - credit
				self.actual_ch = str(balance_from) + " / " + str(balance_to)
				# sel.virtual_ch = str()


		


	# @api.one
	# @api.depends('party')
	# def get_balances(self):
	# 	summary_entry = self.env['summary.entry'].search([('customer','=',self.party.id)])
	# 	summary_clearance= self.env['summary.clearance'].search([('customer','=',self.party.id)])
	# 	journal_lines= self.env['account.move.line'].search([('partner_id','=',self.party.id),('account_id.name','in',["Account Payable","Account Receivable"])])
	# 	journal_lines_actual= self.env['account.move.line'].search([('partner_id','=',self.party.id),('move_id.state','=',"posted")])
	# 	debit = 0
	# 	credit = 0
	# 	for x in journal_lines:
	# 		debit = debit + x.debit
	# 		credit = credit + x.credit
	# 	balance = debit - credit
	# 	debit_actual = 0
	# 	credit_actual = 0
	# 	for x in journal_lines_actual:
	# 		debit_actual = debit_actual + x.debit
	# 		credit_actual = credit_actual + x.credit
	# 	balance_actual = debit_actual - credit_actual
	# 	self.entry_level = summary_entry.net
	# 	# self.clearance_level = summary_clearance.net
	# 	self.virtual_balance = balance
	# 	self.actual_balance = balance_actual


	# @api.one
	# @api.depends('customer','supplier')
	# def get_balances_jv(self):
	# 	summary_entry_customer = self.env['summary.entry'].search([('customer','=',self.customer.id)])
	# 	summary_entry_supplier = self.env['summary.entry'].search([('customer','=',self.supplier.id)])
	# 	summary_clearance_customer = self.env['summary.clearance'].search([('customer','=',self.customer.id)])
	# 	summary_clearance_supplier = self.env['summary.clearance'].search([('customer','=',self.supplier.id)])

	# 	journal_lines_supplier= self.env['account.move.line'].search([('partner_id','=',self.supplier.id),('account_id.name','in',["Account Payable","Account Receivable"])])
	# 	journal_lines_customer= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('account_id.name','in',["Account Payable","Account Receivable"])])
	# 	journal_lines_actual_supplier= self.env['account.move.line'].search([('partner_id','=',self.supplier.id),('account_id.name','in',["Account Payable","Account Receivable"]),('move_id.state','=',"posted")])
	# 	journal_lines_actual_customer= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('account_id.name','in',["Account Payable","Account Receivable"]),('move_id.state','=',"posted")])
		

	# 	debit = 0
	# 	credit = 0
	# 	for y in journal_lines_supplier:
	# 		debit = debit + y.debit
	# 		credit = credit + y.credit
	# 	balance = debit - credit


	# 	debit_customer = 0
	# 	credit_customer = 0
	# 	for z in journal_lines_customer:
	# 		debit_customer = debit_customer + z.debit
	# 		credit_customer = credit_customer + z.credit
	# 	balance_customer = debit_customer - credit_customer


	# 	debit_actual = 0
	# 	credit_actual = 0
	# 	for x in journal_lines_actual_supplier:
	# 		debit_actual = debit_actual + x.debit
	# 		credit_actual = credit_actual + x.credit
	# 	balance_actual = debit_actual - credit_actual


	# 	debit_actual_customer = 0
	# 	credit_actual_customer = 0
	# 	for b in journal_lines_actual_customer:
	# 		debit_actual_customer = debit_actual_customer + b.debit
	# 		credit_actual_customer = credit_actual_customer + b.credit
	# 	balance_actual_customer = debit_actual_customer - credit_actual_customer


	# 	self.entry_level_ch = str(summary_entry_supplier.net)+ " / " +str(summary_entry_customer.net)
	# 	# self.clearance_ch = str(summary_clearance_supplier.net)+ " / " +str(summary_clearance_customer.net)
	# 	self.virtual_ch = str(balance)+ " / " +str(balance_customer)
	# 	self.actual_ch = str(balance_actual)+ " / " +str(balance_actual_customer)









class SummaryEntry(models.Model): 
	_name 		 = 'summary.entry' 
	_description = 'Entry Level Summary'
	# _rec_name = 'date'


	customer = fields.Many2one('res.partner',string = "Party")
	payable = fields.Float()
	receivable = fields.Float()
	net = fields.Float()
	balance = fields.Float(compute = "get_ledger_balances")
	virtual_balance = fields.Float(string = "Virtual Balance",compute = "get_ledger_balances")
	temporary = fields.Float()


	@api.one
	def get_ledger_balances(self):
		entries= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('move_id.state','=',"posted"),('account_id.name','in',["Party Ledgers"])])
		entries_virtual= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('account_id.name','=',"Party Ledgers")])
		debit = 0
		credit = 0
		for x in entries:
			debit = debit + x.debit
			credit = credit + x.credit
		balance = debit - credit

		debit_virtual = 0
		credit_virtual = 0
		for x in entries_virtual:
			debit_virtual = debit_virtual + x.debit
			credit_virtual = credit_virtual + x.credit
		balance_virtual = debit_virtual - credit_virtual
		self.balance = balance
		self.virtual_balance = balance_virtual


class SummaryClearance(models.Model): 
	_name 		 = 'summary.clearance' 
	_description = 'Clearing Level Summary'
	# _rec_name = 'date'


	customer = fields.Many2one('res.partner',string = "Party")
	payable = fields.Float()
	receivable = fields.Float()
	net = fields.Float()
	balance = fields.Float(compute = "get_ledger_balances")
	virtual_balance = fields.Float(string = "Virtual Balance",compute = "get_ledger_balances")



	@api.one
	def get_ledger_balances(self):
		entries= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('move_id.state','=',"posted"),('account_id.name','in',["Party Ledgers"])])
		entries_virtual= self.env['account.move.line'].search([('partner_id','=',self.customer.id),('account_id.name','in',["Party Ledgers"])])

		debit = 0
		credit = 0
		for x in entries:
			debit = debit + x.debit
			credit = credit + x.credit
		balance = debit - credit

		debit_virtual = 0
		credit_virtual = 0
		for x in entries:
			debit_virtual = debit_virtual + x.debit
			credit_virtual = credit_virtual + x.credit
		balance_virtual = debit - credit
		self.balance = balance
		self.virtual_balance = balance_virtual

	



class banks_pakistan(models.Model): 
	_name 		 = 'banks.pakistan'

	name = fields.Char()


class clearance_wizard(models.TransientModel):
	_name = 'clearance.wizard'


	@api.multi
	def sent_for_clearance(self):
		date = datetime.date.today()
		active_class =self.env['funds.flow.tree'].browse(self._context.get('active_ids'))
		for y in active_class:
			if y.stages != "entry":
				raise ValidationError('Entries Must be in Entry Stage')
			else:
				y.date_clearance = date
				y.stages = "clearing"




class confirmation_wizard(models.TransientModel):
	_name = 'confirmation.wizard'

	@api.multi
	def sent_for_confirmed(self):
		active_class =self.env['funds.flow.tree'].browse(self._context.get('active_ids'))

		date = datetime.date.today()

		for y in active_class:
			if y.stages != "clearing":
				raise ValidationError('Entries Must be in Clearance Stage')

			else:			
				y.stages = "confirmation"

				y.date_confirmation = date

				journal_entries = self.env['account.move'].search([('id','=',y.j_entry_id.id)])
				journal_entries.date = date
				journal_entries.post()




class BankandCash(models.Model):
	_inherit = 'account.account'

	bank = fields.Boolean()
	nature                  = fields.Selection([
		('debit', 'Debit'),
		('credit', 'Credit'),
		])


	@api.onchange('user_type_id')
	def get_bank(self):
		if self.user_type_id.name == "Bank and Cash":
			self.bank = True

class CashBookExtension(models.Model):
	_inherit = 'account.bank.statement'

	opening = fields.Float(compute = "get_transaction_balance")
	transactions = fields.Float(compute = "get_transaction_balance")
	funds_flow = fields.Float(string = "Funds Flow")
	closing = fields.Float(compute = "get_transaction_balance")


	@api.onchange('date')
	def get_name(self):
		self.name = str(self.date)



		

	@api.one
	@api.constrains('state','date')
	def RaiseValidation(self):
		records = self.env['account.bank.statement'].search([('state','=',"open"),('id','!=',self.id)])
		if records:
			raise ValidationError('Another Cashbook is already open')

		records = self.env['account.bank.statement'].search([('state','=',"confirm")])
		records.sorted(key=lambda r: r.date)
		recent  = records[0]
		if self.date < recent.date:
			raise ValidationError('Date is less than previous cash book date')
			


	@api.one
	def get_transaction_balance(self):
		total = 0
		for x in self.line_ids:
			total =   total + x.amount
		self.transactions = total

		records = self.env['account.bank.statement'].search([('state','=',"confirm")])
		records.sorted(key=lambda r: r.date)
		recent  = records[0]
		self.opening = recent.closing

		self.closing = self.opening + self.transactions + self.funds_flow






























































####################   Customer Payments #######################################

class customer_payments_sugar(models.Model): 
	_name 		 = 'customer.payments.sugar' 
	_description = 'Customer Payments'
	_rec_name = 'date'


	date = fields.Date(required=True, default=fields.Date.context_today)
	total_amount = fields.Float()
	stages                  = fields.Selection([
		('draft', 'Draft'),
		('posted', 'Posted'),
		],string = "Stages", default = 'draft')

	payments_tree = fields.One2many('customer.payments.tree','customer_payments_id')


	@api.onchange('payments_tree')
	def get_total(self):
		total = 0
		for x in self.payments_tree:
			total = total + x.amount
		self.total_amount = total

	
	@api.multi
	def reset_draft(self):
		self.stages = "draft"


	@api.multi
	def post_entries(self):
		self.stages = "posted"
		journal_entries_lines = self.env['account.move.line'].search([])
		for lines in self.payments_tree:
			journal_entries = self.env['account.move'].search([('customer_payment_id','=',lines.id)])
			if not journal_entries:
				create_journal_entry = journal_entries.create({
						'journal_id': 2,
						'date':self.date,
						'customer_payment_id':lines.id,
						})
				create_debit = journal_entries_lines.create({
					'account_id':lines.bank.id,
					'partner_id':lines.customer.id,
					'name':"Received" + " "+ str(lines.amount) + "  " + "From" + "  "+str(lines.customer.name)+ " in " + str(lines.bank.code)+str(lines.bank.name)+  " "  + str(lines.remarks if lines.remarks else ""), 
					'debit':lines.amount,
					'move_id':create_journal_entry.id
					})
				create_credit = journal_entries_lines.create({
					'account_id':7,
					'partner_id':lines.customer.id,
					'name':"Received" + " "+ str(lines.amount) + "  " + "From" + "  "+str(lines.customer.name)+ " in " + str(lines.bank.code)+str(lines.bank.name)+  " "  + str(lines.remarks if lines.remarks else ""),  
					'credit':lines.amount,
					'move_id':create_journal_entry.id
					})
			else:
				for y in journal_entries.line_ids:
					if y.debit > 0 and y.credit ==0:
						y.account_id = lines.bank.id
						y.partner_id = lines.customer.id
						y.name = "Received" + " "+ str(lines.amount) + "  " + "From" + "  "+str(lines.customer.name)+ " in " + str(lines.bank.code) +str(lines.bank.name)+  " "  + str(lines.remarks if lines.remarks else "")
						y.debit = lines.amount
					else:
						y.partner_id = lines.customer.id
						y.name = "Received" + " "+ str(lines.amount) + "  " + "From" + "  "+str(lines.customer.name)+ " in " + str(lines.bank.code) +str(lines.bank.name)+  " "  + str(lines.remarks if lines.remarks else "")
						y.credit = lines.amount

class customer_payments_tree(models.Model): 
	_name 		 = 'customer.payments.tree'


	customer = fields.Many2one('res.partner', required = True)
	amount = fields.Float()
	bank = fields.Many2one('account.account')
	remarks = fields.Char()

	customer_payments_id = fields.Many2one('customer.payments.sugar')

	@api.multi
	def unlink(self):
		super(customer_payments_tree, self).unlink()

		journal_delete = self.env['account.move'].search([('customer_payment_id','=',self.id)])
		journal_delete.unlink()

		return True

	




####################   Supplier Payments #######################################

class customer_payments_sugar(models.Model): 
	_name 		 = 'supplier.payments.sugar' 
	_description = 'Supplier Payments'
	_rec_name = 'date'


	date = fields.Date(required=True, default=fields.Date.context_today)
	total_amount = fields.Float()
	stages                  = fields.Selection([
		('draft', 'Draft'),
		('posted', 'Posted'),
		],string = "Stages", default = 'draft')

	payments_tree = fields.One2many('supplier.payments.tree','supplier_payments_id')


	@api.onchange('payments_tree')
	def get_total(self):
		total = 0
		for x in self.payments_tree:
			total = total + x.amount
		self.total_amount = total

	@api.multi
	def reset_draft(self):
		self.stages = "draft"
		
	@api.multi
	def post_entries(self):
		self.stages = "posted"
		journal_entries_lines = self.env['account.move.line'].search([])
		for lines in self.payments_tree:
			journal_entries = self.env['account.move'].search([('supplier_payment_id','=',lines.id)])
			if not journal_entries:
				create_journal_entry = journal_entries.create({
						'journal_id': 2,
						'date':self.date,
						'supplier_payment_id':lines.id,
						})
				create_debit = journal_entries_lines.create({
					'account_id':13,
					'partner_id':lines.supplier.id,
					'name':"Paid" + " "+ str(lines.amount) + "  " + "To" + "  "+str(lines.supplier.name), 
					'debit':lines.amount,
					'move_id':create_journal_entry.id
					})
				create_credit = journal_entries_lines.create({
					'account_id':lines.payment_from.id,
					'partner_id':lines.supplier.id,
					'name':"Paid" + " "+ str(lines.amount) + "  " + "To" + "  "+str(lines.supplier.name),  
					'credit':lines.amount,
					'move_id':create_journal_entry.id
					})
			else:
				for y in journal_entries.line_ids:
					if y.credit > 0 and y.debit ==0:
						y.account_id = lines.payment_from.id
						y.partner_id = lines.supplier.id
						y.name = "Paid" + " "+ str(lines.amount) + "  " + "To" + "  "+str(lines.supplier.name) 
						y.credit = lines.amount
						 
					else:
						y.partner_id = lines.supplier.id
						y.name = "Paid" + " "+ str(lines.amount) + "  " + "To" + "  "+str(lines.supplier.name)
						y.debit = lines.amount
						


class supplier_payments_tree(models.Model): 
	_name 		 = 'supplier.payments.tree'


	supplier = fields.Many2one('res.partner',required = True)
	amount = fields.Float()
	bank = fields.Many2one('banks.pakistan')
	remarks = fields.Char()
	payment_from = fields.Many2one('account.account', string = "Payment From")

	supplier_payments_id = fields.Many2one('supplier.payments.sugar')

	@api.multi
	def unlink(self):
		super(supplier_payments_tree, self).unlink()

		journal_delete = self.env['account.move'].search([('supplier_payment_id','=',self.id)])
		journal_delete.unlink()

		return True


class banks_pakistan(models.Model): 
	_name 		 = 'banks.pakistan'

	name = fields.Char()



####################   Inter Party Payments #######################################

class inter_payments_sugar(models.Model): 
	_name 		 = 'inter.payments.sugar' 
	_description = 'Inter Party Payments'
	_rec_name = 'date'


	date = fields.Date(required=True, default=fields.Date.context_today)
	total_amount = fields.Float()
	stages                  = fields.Selection([
		('draft', 'Draft'),
		('posted', 'Posted'),
		],string = "Stages", default = 'draft')

	payments_tree = fields.One2many('inter.payments.tree','inter_payments_id')


	@api.onchange('payments_tree')
	def get_total(self):
		total = 0
		for x in self.payments_tree:
			total = total + x.amount
		self.total_amount = total


	@api.multi
	def reset_draft(self):
		self.stages = "draft"
		
	@api.multi
	def post_entries(self):
		self.stages = "posted"
		journal_entries_lines = self.env['account.move.line'].search([])
		for lines in self.payments_tree:
			journal_entries = self.env['account.move'].search([('inter_payment_id','=',lines.id)])
			if not journal_entries:
				create_journal_entry = journal_entries.create({
						'journal_id': 2,
						'date':self.date,
						'inter_payment_id':lines.id,
						})
				create_debit = journal_entries_lines.create({
					'account_id':13,
					'partner_id':lines.to.id,
					'name':"Payment from" + " "+ str(lines.payment_from.name) + "  " + "To" + "  "+str(lines.to.name), 
					'debit':lines.amount,
					'move_id':create_journal_entry.id
					})
				create_credit = journal_entries_lines.create({
					'account_id':7,
					'partner_id':lines.to.id,
					'name':"Payment from" + " "+ str(lines.payment_from.name) + "  " + "To" + "  "+str(lines.to.name),  
					'credit':lines.amount,
					'move_id':create_journal_entry.id
					})
			else:
				for y in journal_entries.line_ids:
					if y.credit > 0 and y.debit ==0:
						y.partner_id = lines.payment_from.id
						y.name = "Payment from" + " "+ str(lines.payment_from.name) + "  " + "To" + "  "+str(lines.to.name)
						y.credit = lines.amount
						 
					else:
						y.partner_id = lines.to.id
						y.name = "Payment from" + " "+ str(lines.payment_from.name) + "  " + "To" + "  "+str(lines.to.name)
						y.debit = lines.amount

		


class inter_payments_tree(models.Model): 
	_name 		 = 'inter.payments.tree'


	to = fields.Many2one('res.partner',required = True)
	payment_from = fields.Many2one('res.partner',required = True,string = "From")
	amount = fields.Float()
	bank = fields.Many2one('banks.pakistan')
	remarks = fields.Char()

	inter_payments_id = fields.Many2one('inter.payments.sugar')


