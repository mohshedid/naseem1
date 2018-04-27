# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError



########################## Purchase Booking Form ############################################

class purchase_booking(models.Model): 
	_name 		 = 'purchase.booking' 
	_description = 'Booking Module in Purchase'
	# _rec_name = 'str(date)'
	
	date 		 =  fields.Date(required=True, default=fields.Date.context_today, string = "Work Date")
	total 		 =	fields.Float(string="Total Amount")
	total_qty 		 =	fields.Float(string="Total Quantity")
	avg			 =	fields.Float(string="Average")
	user_id      = fields.Many2one('res.users',default=lambda self: self.env.user)
	name         = fields.Char()

	order_line	 =	fields.One2many('purchase.booking.treeview','purchase_booking_id' )
	order_line1	 =	fields.One2many('purchase.booking.treeview','unpaid' )



	@api.one
	@api.constrains('date')
	def single_date(self):

		dates = self.env['purchase.booking'].search([('date','=',self.date),('id','!=',self.id)])
		if dates:
			raise ValidationError('Date Already Exists')


	@api.onchange('date')
	def change_date(self):
		for x in self.order_line:
			x.date = self.date
		for x in self.order_line1:
			x.date = self.date
	







	@api.onchange('order_line','date')
	def get_total(self):
		total = 0
		total_qty = 0
		for x in self.order_line:
			total = total + x.total
			total_qty = total_qty + x.qty
		self.total = total
		self.total_qty = total_qty
		if(self.total_qty>0):
			self.avg = self.total / self.total_qty

		self.name = str(self.user_id.name) + " / "+ str(self.date) 



class purchase_booking_treeview(models.Model):

	_name 		 = 'purchase.booking.treeview'
	_description = 'Tree View of purchase booking'

	supplier	 = fields.Many2one('res.partner',string = "Party")
	# type_transaction = fields.Selection([
	# 	('mill', 'Mill'),
	# 	('supplier', 'Supplier'),
	# 	],string = "Type")
	mill		 = fields.Many2one('product.template')
	qty			 = fields.Float(string="Quantity")
	rate		 = fields.Float(string="Rate")
	total		 = fields.Float(string="Amount",compute ="get_total",store =True)
	# forward      = fields.Boolean()
	maturity_date = fields.Date()
	commission_agent = fields.Many2one('res.partner', string ="Commission Agent")
	com_type = fields.Selection([('no', 'No'),('rec', 'Receive'), ('paid', 'Pay')],string = "Comm Type",default = "no")
	status = fields.Selection([('ready', 'Ready/Hazir'), ('forward', 'Forward')],default = "ready" , string = "Type")
	rate_mp		 = fields.Float(string="Rate MP")
	byana_unit		 = fields.Float(string="Bayana",compute ="get_bayana",store = True)
	date 		 =  fields.Date(required=True, default=fields.Date.context_today)
	comm_amount = fields.Float(string = "Comm Amount",compute ="get_total",store =True)
	comm_rate = fields.Float(string = "Comm Rate")
	purchase_booking_id = fields.Many2one('purchase.booking')
	unpaid = fields.Many2one('purchase.booking')



	@api.one
	@api.depends('rate_mp','qty','rate')
	def get_bayana(self):
		self.byana_unit = (self.rate - self.rate_mp) * self.qty



	@api.onchange('supplier')
	def get_date(self):
		if self.purchase_booking_id:
			date = self.purchase_booking_id.date
		if self.unpaid:
			date = self.unpaid.date
		self.date = date




	@api.onchange('commission_agent','com_type')
	def get_commission_rate(self):
		self.comm_rate = self.commission_agent.comm_rate
		if self.com_type == "no":
			self.comm_rate = 0

	@api.one
	@api.depends('qty','rate','comm_rate','commission_agent')
	def get_total(self):
		self.total = self.qty * self.rate
		self.comm_amount = self.qty * self.comm_rate



	@api.model
	def create(self, vals):

		new_record = super(purchase_booking_treeview, self).create(vals)

		if new_record.status == "ready":
			purchase = self.env['purchase.sugar'].search([])
			generate_purchase_form = purchase.create({
				'supplier': new_record.supplier.id,
				'mill':new_record.mill.id,
				'rate':new_record.rate,
				'qty':new_record.qty,
				'total':new_record.total,
				'p_booking_id':new_record.id,
				'date':new_record.date,
				'status':new_record.status,
				})


		if new_record.status == "forward":
			contract = self.env['forward.contract'].search([('maturity_date','=',new_record.maturity_date),('mill','=',new_record.mill.id),('party','=',new_record.supplier.id)])
			if not contract:
				create_contract = contract.create({
					'maturity_date': new_record.maturity_date,
					'mill':new_record.mill.id,
					'party':new_record.supplier.id,
					'name':str(new_record.maturity_date) + " " + str(new_record.mill.name)
					})
				create_contract_lines = self.env['forward.purchases'].search([]).create({
					'date': new_record.date,
					'supplier': new_record.supplier.id,
					'qty':new_record.qty,
					'rate':new_record.rate,
					'total':new_record.total,
					'forward_contract_id':create_contract.id,
					'purchase_id':new_record.id,
					})
			else:
				create_contract_lines = self.env['forward.purchases'].search([]).create({
					'date': new_record.date,
					'supplier': new_record.supplier.id,
					'qty':new_record.qty,
					'rate':new_record.rate,
					'total':new_record.total,
					'forward_contract_id':contract.id,
					'purchase_id':new_record.id,
					})



		return new_record

	@api.multi
	def write(self, vals):
		before_write = self.qty
		purchase = self.env['purchase.sugar'].search([('p_booking_id','=',self.id)])
		purchase.unlink()
		super(purchase_booking_treeview, self).write(vals)
		after_write = self.qty
		difference =  after_write - before_write

		if self.status == "ready":
			purchase = self.env['purchase.sugar'].search([])
			generate_purchase_form = purchase.create({
				'supplier': self.supplier.id,
				'mill':self.mill.id,
				'rate':self.rate,
				'qty':self.qty,
				'total':self.total,
				'p_booking_id':self.id,
				'date':self.date,
				'status':self.status,
				})
		


		if self.status == "forward":
			relevant_contract = self.env['forward.purchases'].search([('purchase_id','=',self.id)])
			relevant_contract.unlink()
			contract = self.env['forward.contract'].search([('maturity_date','=',self.maturity_date),('mill','=',self.mill.id),('party','=',self.supplier.id)])
			if not contract:
				create_contract = contract.create({
					'maturity_date': self.maturity_date,
					'mill':self.mill.id,
					'party':self.supplier.id,
					})
				create_contract_lines = self.env['forward.purchases'].search([]).create({
					'date': self.date,
					'supplier': self.supplier.id,
					'qty':self.qty,
					'rate':self.rate,
					'total':self.total,
					'purchase_id':self.id,
					'forward_contract_id':create_contract.id,
					})
			else:
				create_contract_lines = self.env['forward.purchases'].search([]).create({
					'date': self.date,
					'supplier': self.supplier.id,
					'qty':self.qty,
					'rate':self.rate,
					'total':self.total,
					'purchase_id':self.id,
					'forward_contract_id':contract.id,
					})
		return True


	@api.multi
	def unlink(self):

		relevant_contract = self.env['forward.purchases'].search([('purchase_id','=',self.id)])
		relevant_contract.unlink()

		
		super(purchase_booking_treeview, self).unlink()

		purchase_delivery = self.env['purchase.sugar'].search([('p_booking_id','=',self.id)])
		purchase_delivery.unlink()




		return True

	# @api.onchange('qty','rate')
	# def get_total(self):
	# 	self.total = self.qty * self.rate

############################### Purchase Main Form #####################################

class purchase_sugar(models.Model): 
	_name 		 = 'purchase.sugar' 
	_description = 'Purchase delivery Sugar industry'
	_rec_name = 'order_no'

	supplier	 = fields.Many2one('res.partner',string ="Party")
	mill		 = fields.Many2one('product.template')
	rate		 = fields.Float(string="Rate")
	qty			 = fields.Float(string="Quantity")
	status = fields.Selection([('ready', 'Ready/Hazir'), ('forward', 'Forward')],default = "ready" , string = "Type")
	total		 = fields.Float(string="Total")
	# delivered		 = fields.Float(string="Delivered")
	# remaining		 = fields.Float(string="Remaining")
	date 		 =  fields.Date(required=True)
	p_booking_id        =  fields.Integer()
	# purchase_tree_loading = fields.One2many('purchase.sugar.tree','purchase_id')
	# adda_tree = fields.One2many('adda.tree','purchase_id')
	order_no = fields.Char(index=True, readonly=True)




	





	@api.onchange('qty','rate')
	def get_total(self):
		self.total = self.qty * self.rate

	@api.model
	def create(self, vals):
		vals['order_no'] = self.env['ir.sequence'].next_by_code('purchase.sugar')
		new_record = super(purchase_sugar, self).create(vals)



		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',new_record.mill.id)])
		for x in relevant_summary:
			x.qty = x.qty + new_record.qty
			x.for_sale = x.qty - x.amanat


		if new_record.supplier.mill == True:
			relevant_mill = self.env['mill.wise'].search([('mill','=',new_record.supplier.id),('brand','=',new_record.mill.id)])
			if not relevant_mill:
				raise ValidationError('Associate brand with the mill')
			else:
				for x in relevant_mill:
					x.total_purchase = x.total_purchase + new_record.qty
					x.remaining = x.total_purchase - x.loaded

		remaining_transfers = self.env['remaining.transfers'].search([('supplier','=',new_record.supplier.id),('mill','=',new_record.mill.id)])
		if not remaining_transfers:
			create_entry = remaining_transfers.create({
					'supplier':new_record.supplier.id,
					'mill':new_record.mill.id,
					'purchased':new_record.qty,
					# 'received':new_record.id,
					'remaining':new_record.qty,
					})
		else:
			remaining_transfers.purchased = remaining_transfers.purchased + new_record.qty
			remaining_transfers.remaining = remaining_transfers.purchased - remaining_transfers.received

		amanats = self.env['amanats'].search([('mill','=',new_record.mill.id),('customer','=',new_record.supplier.id)])
		if not amanats:
			create_amanat = amanats.create({
				'customer': new_record.supplier.id,
				'mill':new_record.mill.id,
				})
		amanats = self.env['amanats'].search([('mill','=',new_record.mill.id),('customer','=',new_record.supplier.id)])
		for x in amanats:
			x.purchases = x.purchases + new_record.qty
			x.amanat = (x.sales - x.purchases) - (x.delivered - x.received) + x.amanat_transfers



		# stock_history = self.env['stock.history.sugar'].search([])
		# create_stock_history = stock_history.create({
		# 		'mill':new_record.mill.id,
		# 		'qty':new_record.qty,
		# 		'date':new_record.date,
		# 		'purchase_id':new_record.id,
		# 		'party':new_record.supplier.id,
		# 		'ref_no':new_record.order_no,
		# 		'type_transaction':"Purchase"
		# 		})



		journal = self.env['account.journal'].search([('name','=',"Purchase")])
		purchase_account = self.env['account.account'].search([('name','=',"Purchases")])
		party_ledger = self.env['account.account'].search([('name','=',"Party Ledger")])

		journal_entries = self.env['account.move'].search([])
		journal_entries_lines = self.env['account.move.line'].search([])
		create_journal_entry = journal_entries.create({
				'journal_id': journal.id,
				'date':new_record.date,
				'ref':new_record.order_no,
				'name':new_record.order_no
				})
		create_debit = journal_entries_lines.create({
			'account_id':purchase_account.id,
			'partner_id':new_record.supplier.id,
			'name':str(new_record.mill.name) + " "+ str(new_record.qty) + " @ " + str(new_record.rate), 
			'debit':new_record.total,
			'move_id':create_journal_entry.id
			})
		create_credit = journal_entries_lines.create({
			'account_id':party_ledger.id,
			'partner_id':new_record.supplier.id,
			'name':str(new_record.mill.name) + " "+ str(new_record.qty) + " @ " + str(new_record.rate), 
			'credit':new_record.total,
			'move_id':create_journal_entry.id
			})



		return new_record

	@api.multi
	def write(self, vals):


		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		for x in relevant_summary:
			x.qty = x.qty - self.qty
			x.for_sale = x.qty - x.amanat

		relevant_mill = self.env['mill.wise'].search([('mill','=',self.supplier.id),('brand','=',self.mill.id)])
		for x in relevant_mill:
			x.total_purchase = x.total_purchase - self.qty
			x.remaining = x.total_purchase - x.loaded

		before_write = self.qty
		remaining_transfers = self.env['remaining.transfers'].search([('supplier','=',self.supplier.id),('mill','=',self.mill.id)])
		for x in remaining_transfers:
			x.purchased = x.purchased - self.qty
			x.remaining = x.purchased - x.received
		super(purchase_sugar, self).write(vals)
		after_write = self.qty
		difference = after_write - before_write
		remaining_transfers = self.env['remaining.transfers'].search([('supplier','=',self.supplier.id),('mill','=',self.mill.id)])
		for x in remaining_transfers:
			x.purchased = x.purchased + self.qty
			x.remaining = x.purchased - x.received

		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		for x in relevant_summary:
			x.qty = x.qty + self.qty
			x.for_sale = x.qty - x.amanat



		if self.supplier.mill == True:
			relevant_mill = self.env['mill.wise'].search([('mill','=',self.supplier.id),('brand','=',self.mill.id)])
			if not relevant_mill:
				raise ValidationError('Associate brand with the mill')
			else:
				for x in relevant_mill:
					x.total_purchase = x.total_purchase + self.qty
					x.remaining = x.total_purchase - x.loaded


		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.supplier.id)])
		for x in amanats:
			x.purchases = x.purchases + difference



		# stock_history = self.env['stock.history.sugar'].search([('purchase_id','=',self.id)])
		# print stock_history
		# stock_history.mill = self.mill.id
		# stock_history.qty = self.qty
		# stock_history.date = self.date
		# stock_history.party = self.supplier.id
		# stock_history.ref_no = self.order_no

		journal_entry = self.env['account.move'].search([('ref','=',self.order_no)])
		print journal_entry
		
		journal_entry.date = self.date

		journal_entry_line = self.env['account.move.line'].search([('move_id.ref','=',self.order_no)])
		for x in journal_entry_line:
			print x.id
			x.partner_id = self.supplier.id
			x.name = self.mill.name + " "+ str(self.qty) + " @ " + str(self.rate)
			if x.debit > 0:
				x.debit = self.total
			elif x.credit > 0:
				x.credit = self.total
		return True

	@api.multi
	def unlink(self):

		# stock_history = self.env['stock.history.sugar'].search([('purchase_id','=',self.id)])
		# stock_history.unlink()

		journal_entry = self.env['account.move'].search([('ref','=',self.order_no)])
		journal_entry.unlink()


		relevant_mill = self.env['mill.wise'].search([('mill','=',self.supplier.id),('brand','=',self.mill.id)])
		for x in relevant_mill:
			x.total_purchase = x.total_purchase - self.qty
			x.remaining = x.total_purchase - x.loaded

		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		for x in relevant_summary:
			relevant_summary.qty = relevant_summary.qty - self.qty
			x.for_sale = x.qty - x.amanat		



		remaining_transfers = self.env['remaining.transfers'].search([('supplier','=',self.supplier.id),('mill','=',self.mill.id)])
		for x in remaining_transfers:
			x.purchased = x.purchased - self.qty
			x.remaining = x.purchased - x.received


		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.supplier.id)])
		for x in amanats:
			x.purchases = x.purchases - self.qty
			x.amanat = (x.sales - x.purchases) - (x.delivered - x.received) + x.amanat_transfers

		super(purchase_sugar, self).unlink()

		return True











		