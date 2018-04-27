# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError


####################   Sales Booking Main Form #######################################

class sale_booking(models.Model): 
	_name 		 = 'sales.booking' 
	_description = 'Booking Module in Sales'
	# _rec_name = 'date_string'
	
	date 		 =  fields.Date(required=True, default=fields.Date.context_today, string ="Work Date")
	total 		 =	fields.Float(string="Total Amount",compute = "get_total",store = True)
	total_qty 	 =	fields.Float(string="Total Quantity",compute = "get_total",store = True)
	avg			 =	fields.Float(string="Average",compute = "get_total",store = True)
	user_id      = 	fields.Many2one('res.users',default=lambda self: self.env.user)
	name 		 = 	fields.Char()
	check 		 = 	fields.Boolean(compute = "check_box",default = True)
	mills 		 = 	fields.Many2many('product.product')


	order_line	 =	fields.One2many('sale.booking.treeview','sales_booking_id')
	order_line1	 =	fields.One2many('sale.booking.treeview','unpaid')

	@api.one
	def check_box(self):
		self.check = True

	@api.one
	@api.depends('order_line','date')
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

	@api.one
	@api.constrains('date')
	def single_date(self):
		dates = self.env['sales.booking'].search([('date','=',self.date),('id','!=',self.id)])
		if dates:
			raise ValidationError('Date Already Exists')


	@api.onchange('order_line')
	def change_temporary(self):
		if self.order_line:
			self.check = False
			products = []
			for x in self.order_line:
				if x.status == "ready":
					if not x.id:
						if x.mill.id not in products:
							products.append(x.mill.id)

			print products

			mills_field = []
			for x in self.mills:
				mills_field.append(x.id)

			for x in products:
				if x not in mills_field:
					mills_field.append(x)

			self.mills = mills_field
			
			for x in self.mills:
				total = 0
				for y in self.order_line:
					if not y.id and y.status == "ready":
						if y.mill.id == x.id:
							total = total + y.qty

				summary = self.env['stock.summary.sugar'].search([('mill','=',x.id)])
				summary.write({'temporary':total})




	# @api.model
	# def create(self, vals):

	# 	new_record = super(sale_booking, self).create(vals)
		
	# 	summary = self.env['stock.summary.sugar'].search([])
	# 	for x in summary:
	# 		summary.write({'temporary':0})

	# 	return new_record


	# @api.multi
	# def write(self, vals):
	# 	summary = self.env['stock.summary.sugar'].search([])
	# 	for x in summary:
	# 		summary.write({'temporary':0})
	# 	super(sale_booking, self).write(vals)

	# 	return True






class sale_booking_treeview(models.Model):

	_name 		 = 'sale.booking.treeview'
	_description = 'Tree View of sales booking'

	customer	 = fields.Many2one('res.partner',required=True,string = "Party")
	mill		 = fields.Many2one('product.template',required=True)
	qty			 = fields.Float(string="Quantity")
	rate		 = fields.Float(string="Rate")
	date 		 =  fields.Date(required=True, default=fields.Date.context_today)
	total		 = fields.Float(string="Amount", compute ="get_total",store = True)
	rate_mp		 = fields.Float(string="Rate MP")
	available_sale		 = fields.Float(string="AFS", readonly = True)
	byana_unit		 = fields.Float(string="Bayana",compute ="get_bayana",store = True)
	maturity_date = fields.Date()
	status = fields.Selection([('ready', 'Ready/Hazir'), ('forward', 'Forward')],default = "ready" )
	commission_agent = fields.Many2one('res.partner', string ="Commission Agent")
	com_type = fields.Selection([('no', 'No'),('rec', 'Received'), ('paid', 'Paid')],string = "Comm Rate",default = "no")
	comm_amount = fields.Float(string = "Comm Amount", compute ="get_total",store = True)
	comm_rate = fields.Float(string = "Comm Rate")
	sales_booking_id = fields.Many2one('sales.booking')
	unpaid = fields.Many2one('sales.booking')









	@api.onchange('commission_agent','com_type')
	def get_commission_rate(self):
		self.comm_rate = self.commission_agent.comm_rate
		if self.com_type == "no":
			self.comm_rate = 0

	@api.onchange('customer')
	def get_date(self):
		if self.sales_booking_id:
			date = self.sales_booking_id.date
		if self.unpaid:
			date = self.unpaid.date
		self.date = date

	# @api.one
	# @api.depends('mill')

	@api.onchange('mill')
	def get_for_sale(self):
		for_sale = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		if self.sales_booking_id.check == True:

			self.available_sale = for_sale.for_sale
		else:
			self.available_sale = for_sale.for_sale - for_sale.temporary

		

	@api.one
	@api.depends('qty','rate','comm_rate','commission_agent')
	def get_total(self):
		self.total = self.qty * self.rate
		self.comm_amount = self.qty * self.comm_rate

	@api.one
	@api.depends('rate_mp','qty','rate')
	def get_bayana(self):
		self.byana_unit = (self.rate - self.rate_mp) * self.qty
		





	@api.model
	def create(self, vals):

		new_record = super(sale_booking_treeview, self).create(vals)
		if new_record.status == "ready":
			sales = self.env['sales.sugar'].search([])
			generate_sales_form = sales.create({
				'customer': new_record.customer.id,
				'mill':new_record.mill.id,
				'rate':new_record.rate,
				'qty':new_record.qty,
				'total':new_record.total,
				'booking_id':new_record.id,
				'date':new_record.date,
				'status':new_record.status,
				'remaining':new_record.qty
				})

			if new_record.com_type != "no":
				commission = self.env['sugar.commission'].search([])

				generate_commission = commission.create({
					'party': new_record.customer.id,
					'mill':new_record.mill.id,
					'rate':new_record.rate,
					'qty':new_record.qty,
					'total':new_record.total,
					'date':new_record.date,
					'transaction_type':"Sale",
					'commission_agent':new_record.commission_agent.id,
					'comm_type':new_record.com_type,
					'comm_amount':new_record.comm_amount,
					'comm_rate':new_record.comm_rate,
					'sale_id':new_record.id,
					})






		if new_record.status == "forward":
			contract = self.env['forward.contract'].search([('maturity_date','=',new_record.maturity_date),('mill','=',new_record.mill.id),('party','=',new_record.customer.id)])
			if not contract:
				create_contract = contract.create({
					'maturity_date': new_record.maturity_date,
					'mill':new_record.mill.id,
					'party':new_record.customer.id,
					'name':str(new_record.maturity_date) + " " + str(new_record.mill.name)
					})
				create_contract_lines = self.env['forward.sales'].search([]).create({
					'date': new_record.date,
					'customer': new_record.customer.id,
					'qty':new_record.qty,
					'rate':new_record.rate,
					'total':new_record.total,
					'forward_contract_id':create_contract.id,
					'sale_id':new_record.id,
					})
			else:
				create_contract_lines = self.env['forward.sales'].search([]).create({
					'date': new_record.date,
					'customer': new_record.customer.id,
					'qty':new_record.qty,
					'rate':new_record.rate,
					'total':new_record.total,
					'forward_contract_id':contract.id,
					'sale_id':new_record.id,

					})


		return new_record

	@api.multi
	def write(self, vals):
		sales = self.env['sales.sugar'].search([('booking_id','=',self.id)])
		sales.unlink()
		super(sale_booking_treeview, self).write(vals)


		if self.status == "ready":
			sales = self.env['sales.sugar'].search([])
			generate_sales_form = sales.create({
				'customer': self.customer.id,
				'mill':self.mill.id,
				'rate':self.rate,
				'qty':self.qty,
				'total':self.total,
				'booking_id':self.id,
				'status':self.status,
				'date':self.date,
				'remaining':self.qty
				})







		if self.status == "forward":
			relevant_contract = self.env['forward.sales'].search([('sale_id','=',self.id)])
			relevant_contract.unlink()
			contract = self.env['forward.contract'].search([('maturity_date','=',self.maturity_date),('mill','=',self.mill.id),('party','=',self.customer.id)])
			if not contract:
				create_contract = contract.create({
					'maturity_date': self.maturity_date,
					'mill':self.mill.id,
					'party':self.customer.id,
					})
				create_contract_lines = self.env['forward.sales'].search([]).create({
					'date': self.date,
					'customer': self.customer.id,
					'qty':self.qty,
					'rate':self.rate,
					'total':self.total,
					'sale_id':self.id,
					'forward_contract_id':create_contract.id,
					})
			else:
				create_contract_lines = self.env['forward.sales'].search([]).create({
					'date': self.date,
					'customer': self.customer.id,
					'qty':self.qty,
					'rate':self.rate,
					'total':self.total,
					'sale_id':self.id,
					'forward_contract_id':contract.id,
					})




		return True

	@api.multi
	def unlink(self):
		super(sale_booking_treeview, self).unlink()

		relevant_contract = self.env['forward.sales'].search([('sale_id','=',self.id)])
		relevant_contract.unlink()


		sales_delivery = self.env['sales.sugar'].search([('booking_id','=',self.id)])
		sales_delivery.unlink()

		return True

###########################     Sales Main Form   ################################

class sale_sugar(models.Model): 
	_name 		 = 'sales.sugar' 
	_description = 'Sales delivery Sugar industry'
	_rec_name = 'order_no'

	customer	 = fields.Many2one('res.partner' , readonly = True,string = "Party")
	mill		 = fields.Many2one('product.template', readonly = True)
	rate		 = fields.Float(string="Rate", readonly = True)
	qty			 = fields.Float(string="Quantity" , readonly = True)
	total		 = fields.Float(string="Total" , readonly = True)
	status       = fields.Selection([('ready', 'Ready/Hazir'), ('forward', 'Forward')],default = "ready" )
	date 		 =  fields.Date(required=True, readonly = True,string ="Work Date")

	booking_id   = fields.Char()
	order_no = fields.Char(index=True, readonly=True)

	order_line	 =	fields.One2many('sale.sugar.treeview','sales_sugar_id')



	@api.model
	def create(self, vals):
		vals['order_no'] = self.env['ir.sequence'].next_by_code('sales.sugar')
		
		new_record = super(sale_sugar, self).create(vals)

		amanat_supplier = self.env['res.partner'].search([('name','=',"Amanat")])

		
		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',new_record.mill.id)])

		for x in relevant_summary:
			x.amanat = x.amanat + new_record.qty
			x.for_sale = x.qty - x.amanat		


		# mill_wise = self.env['mill.wise'].search([('brand','=',new_record.mill.id)])
		# if not mill_wise:
		# 	pass
		# 	raise ValidationError('Associate brand with the mill')
		# else:
		# 	for x in mill_wise:
		# 		x.total_sale = x.total_sale + new_record.qty
		# 		x.amanat = x.amanat + new_record.qty


		amanats = self.env['amanats'].search([('mill','=',new_record.mill.id),('customer','=',new_record.customer.id)])
		if not amanats:
			create_amanat = amanats.create({
				'customer': new_record.customer.id,
				'mill':new_record.mill.id 
				})
		amanats = self.env['amanats'].search([('mill','=',new_record.mill.id),('customer','=',new_record.customer.id)])
		for x in amanats:
			x.sales = x.sales + new_record.qty
			x.amanat = (x.sales - x.purchases) - (x.delivered - x.received) + x.amanat_transfers
			



		
		


		journal = self.env['account.journal'].search([('name','=',"Sale")])
		sale_account = self.env['account.account'].search([('name','=',"Sales")])
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
			'account_id':party_ledger.id,
			'partner_id':new_record.customer.id,
			'name':str(new_record.mill.name) + " "+ str(new_record.qty) + " @ " + str(new_record.rate), 
			'debit':new_record.total,
			'move_id':create_journal_entry.id
			})
		create_credit = journal_entries_lines.create({
			'account_id':sale_account.id,
			'partner_id':new_record.customer.id,
			'name':new_record.mill.name + " "+ str(new_record.qty) + " @ " + str(new_record.rate), 
			'credit':new_record.total,
			'move_id':create_journal_entry.id
			})


		return new_record

	@api.multi
	def write(self, vals):
		before_write = self.qty

		mill_wise = self.env['mill.wise'].search([('brand','=',self.mill.id)])
		for x in mill_wise:
			x.total_sale = x.total_sale -self.qty
			x.amanat = x.amanat - self.qty

		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.customer.id)])
		for x in amanats:
			x.sales = x.sales - self.qty
			x.amanat = (x.sales - x.purchases) - (x.delivered - x.received) + x.amanat_transfers


		super(sale_sugar, self).write(vals)

		amanat_supplier = self.env['res.partner'].search([('name','=',"Amanat")])




		after_write = self.qty
		difference =  after_write - before_write
		# relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		# for x in relevant_summary:
		# 	x.amanat = x.amanat + difference


		# mill_wise = self.env['mill.wise'].search([('brand','=',self.mill.id)])
		# if not mill_wise:
		# 	pass
		# 	raise ValidationError('Associate brand with the mill')
		# else:
		# 	for x in mill_wise:
		# 		x.total_sale = x.total_sale + self.qty
		# 		x.amanat = x.amanat + self.qty


		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.customer.id)])
		if not amanats:
			create_amanat = amanats.create({
				'customer': self.customer.id,
				'mill':self.mill.id 
				})
		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.customer.id)])
		for x in amanats:
			x.sales = x.sales + self.qty
			x.amanat = (x.sales - x.purchases) - (x.delivered - x.received) + x.amanat_transfers


			

		journal_entry = self.env['account.move'].search([('ref','=',self.order_no)])
		
		journal_entry.date = self.date

		journal_entry_line = self.env['account.move.line'].search([('move_id.ref','=',self.order_no)])
		for x in journal_entry_line:
			print x.id
			x.partner_id = self.customer.id
			x.name = self.mill.name + " "+ str(self.qty) + " @ " + str(self.rate)
			if x.debit > 0:
				x.debit = self.total
			elif x.credit > 0:
				x.credit = self.total




		return True

	@api.multi
	def unlink(self):

		journal_entry = self.env['account.move'].search([('ref','=',self.order_no)])
		journal_entry.unlink()

		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.customer.id)])
		for x in amanats:
			x.sales = x.sales - self.qty
			x.amanat = (x.sales - x.purchases) - (x.delivered - x.received) + x.amanat_transfers



		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		for x in relevant_summary:
			relevant_summary.amanat = relevant_summary.amanat - self.qty
			x.for_sale = x.qty - x.amanat		



		mill_wise = self.env['mill.wise'].search([('brand','=',self.mill.id)])
		for x in mill_wise:
			x.total_sale = x.total_sale - self.qty
			x.amanat = x.amanat - self.qty


		super(sale_sugar, self).unlink()

		return True



class sale_sugar_treeview(models.Model):

	_name 		 = 'sale.sugar.treeview'
	_description = 'Tree View of sales module sugar industry'

	customer            = fields.Many2one('res.partner')
	delivery_from		= fields.Many2one('res.partner')
	qty_del				= fields.Float(string="Quantity Delivered")
	date				= fields.Date(required=True,default=fields.Date.context_today)
	sales_sugar_id      = fields.Many2one('sales.sugar')
	adda      = fields.Many2one('adda')
	loading_id          = fields.Many2one('loading.sugar.tree')
	

	@api.model
	def create(self, vals):

		new_record = super(sale_sugar_treeview, self).create(vals)


		
		
	 
		return new_record

	@api.multi
	def write(self, vals):
		before_write = self.qty_del
		super(sale_sugar_treeview, self).write(vals)
		after_write = self.qty_del

		print before_write
		print after_write


		ref_no = self.sales_sugar_id.order_no

		return True

	@api.multi
	def unlink(self):


		super(sale_sugar_treeview, self).unlink()
		

		return True



