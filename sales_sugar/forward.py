# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError







class ForwardContract(models.Model): 
	_name 		 = 'forward.contract' 
	_description = 'Forward Contract'
	# _rec_name = 'str(date)'
	
	name = fields.Char()
	maturity_date    	 =  fields.Date(readonly = True)
	mill 		     	 =	fields.Many2one('product.product',readonly = True)
	party 		     	 =	fields.Many2one('res.partner',readonly = True)
	total_sales      	 = fields.Float(readonly = True,string = "Total Sales Amount")
	total_purchases  	 = fields.Float(readonly = True,string = "Total Purchases Amount")
	net_qty          	 = fields.Float(readonly = True ,string = "Net Quantity")
	net_amount       	 = fields.Float(readonly = True,string = "Net Amount ")
	average_price       	 = fields.Float(readonly = True,string = "Average Price ")
	total_sales_qty       	 = fields.Float(readonly = True,string = "Total Sales Qty")
	total_purchase_qty       	 = fields.Float(readonly = True,string = "Total Purchase Qty ")
	total_amount       	 = fields.Float(readonly = True,string = "Total Amount ")

	contract_trial_id       	 = fields.Many2one('contract.trial')

	forward_purchase	 =	fields.One2many('forward.purchases','forward_contract_id' )
	forward_sale	     =	fields.One2many('forward.sales','forward_contract_id' )
	hawala	             =	fields.One2many('forward.hawala','forward_contract_id' )
	settlement	         =	fields.One2many('contract.settlement','forward_contract_id' )
	settlement_summary	 =	fields.One2many('contract.settlement.summary','forward_contract_id' )


	@api.multi
	def create_settlement(self):
		for x in self.settlement:
			x.unlink()
		for x in self.settlement_summary:
			x.unlink()
		for x in self.forward_purchase:
			self.create_settlement_entries("purchase",x.supplier.id,x.rate,x.qty,x.date,None)	

		for x in self.forward_sale:
			self.create_settlement_entries("sale",x.customer.id,x.rate,x.qty,x.date,None)		

		for x in self.hawala:
			if x.to == self.party:
				self.create_settlement_entries("sale",x.to.id,x.rate,x.qty,x.date,x.from_party.id)
			elif x.from_party == self.party:		
				self.create_settlement_entries("purchase",x.from_party.id,x.rate,x.qty,x.date,x.to.id)

		total_purchases = 0
		total_sales = 0
		total_purchases_amount = 0
		total_sales_amount = 0
		for x in self.settlement:
			if x.types == "purchase":
				total_purchases = total_purchases + x.qty
				total_purchases_amount = total_purchases_amount + (x.qty * x.rate)
			if x.types == "sale":
				total_sales_amount = total_sales_amount + (x.qty * x.rate)
				total_sales = total_sales + x.qty

		self.total_sales = total_sales_amount
		self.total_purchases = total_purchases_amount
		self.net_qty =  total_purchases - total_sales
		self.average_price = (total_purchases_amount - total_sales_amount)/ self.net_qty
		self.average_price = abs(self.average_price)
		if self.net_qty < 0:
			self.total_sales_qty = abs(self.net_qty)
			self.total_amount = self.total_sales_qty * self.average_price 
		if self.net_qty > 0:
			self.total_purchase_qty = abs(self.net_qty)
			self.total_amount = self.total_sales_qty * self.average_price


		for rem in self.settlement:
			rem.remaining = rem.qty - rem.settled_quantity
		

		settlements = self.env['contract.settlement'].search([('forward_contract_id','=',self.id)])
		for x in self.settlement:
			if x.types == "purchase" and x.remaining > 0:
				adjustable_qty = x.remaining 
				for y in self.settlement:
					if adjustable_qty > 0:
						if y.types == "sale" and y.remaining > 0:
							if adjustable_qty > y.remaining:
								y.settled_quantity = y.settled_quantity +  y.remaining
								adjustable_qty = adjustable_qty - y.remaining
								x.settled_quantity = x.settled_quantity + y.remaining
								self.create_adjustements(x.number,y.remaining,y.rate,y.id)
								self.create_adjustements(y.number,y.remaining,y.rate,x.id)

							else:
								y.settled_quantity = y.settled_quantity + adjustable_qty
								x.settled_quantity = x.settled_quantity + adjustable_qty

								self.create_adjustements(x.number,adjustable_qty,y.rate,y.id)
								self.create_adjustements(y.number,adjustable_qty,y.rate,x.id)

								adjustable_qty = adjustable_qty - y.remaining

							for rem in self.settlement:
								rem.remaining = rem.qty - rem.settled_quantity
			adj_records = self.env['contract.adjustments'].search([('settlement_id','=',x.id)])
			adj = []
			for rec in adj_records:
				adj.append(rec.id)
			x.adjustment = adj

			if x.types == "purchase":
				amount = 0
				for diff in x.adjustment:
					payable = diff.qty * x.rate
					recievable = diff.qty * diff.rate
					difference = recievable - payable
					amount = amount + difference
				x.set_rate = amount

		for x in self.settlement:
			if x.remaining > 0:
				self.env['contract.settlement.summary'].search([]).create({
							'date' : x.date,
							'number': x.number,
							'types': x.types,
							'party': x.party.id,
							'rate' : x.rate,
							'qty'	: x.qty,
							'settled_quantity' : x.settled_quantity,
							'set_rate' : x.set_rate,
							'adjustment' : x.adjustment,
							'remaining' : x.remaining,
							'forward_contract_id': x.forward_contract_id.id
					})
		total_difference = 0
		for x in self.settlement:
			total_difference = total_difference + x.set_rate
		self.net_amount = total_difference


		

	@api.multi
	def create_settlement_entries(self,types,party,rate,qty,date,hawala_ref):
		self.env['contract.settlement'].search([]).create({
					'types': types,
					'party':party,
					'rate':rate,
					'qty':qty,
					'date':date,
					'forward_contract_id':self.id,
					'hawala_ref':hawala_ref,
					})

	@api.multi
	def create_adjustements(self,number,qty,rate,settlement_id):
		self.env['contract.adjustments'].search([]).create({
					'number': number,
					'qty':qty,
					'rate':rate,
					'settlement_id':settlement_id,
					})

	


class ForwardPurchases(models.Model):

	_name 		 = 'forward.purchases'
	_description = 'Tree View of Forward Purchases'

	date         	= fields.Date()
	supplier	 	= fields.Many2one('res.partner',string = "Party")
	qty			 	= fields.Float(string="Quantity")
	rate		 	= fields.Float(string="Rate")
	total		 	= fields.Float(string="Total")
	purchase_id		 	= fields.Many2one('purchase.booking.treeview')
	forward_contract_id = fields.Many2one('forward.contract')


class ForwardSales(models.Model):

	_name 		 = 'forward.sales'
	_description = 'Tree View of Forward Sales'

	date         = fields.Date()
	customer	 = fields.Many2one('res.partner',string = "Party")
	qty			 = fields.Float(string="Quantity")
	rate		 = fields.Float(string="Rate")
	total		 = fields.Float(string="Total")
	sale_id		 = fields.Many2one('sale.booking.treeview')
	forward_contract_id = fields.Many2one('forward.contract')

class ForwardHawala(models.Model): 
	_name 		 = 'forward.hawala' 
	_description = 'Hawala'

	
	date = fields.Date(default=fields.Date.context_today,string ="Work Date")
	contract =  fields.Many2one('forward.contract')
	from_party = fields.Many2one('res.partner',string = "From")
	to = fields.Many2one('res.partner')
	rate = fields.Float()
	qty = fields.Float()
	amount = fields.Float()
	hawala_id = fields.Many2one('hawala.lines')


	forward_contract_id	 =	fields.Many2one('forward.contract' )






class ContractSettlement(models.Model):

	_name 		 = 'contract.settlement'
	_description = 'Tree View of Contract Settlement'


	@api.model
	def create(self, vals):
		vals['number'] = self.env['ir.sequence'].next_by_code('contract.settlement')
		new_record = super(ContractSettlement, self).create(vals)
		

		return new_record


	date = fields.Date()
	number = fields.Char()
	types                  = fields.Selection([
		('sale', 'Sale'),
		('purchase', 'Purchase'),
		],string = "Type")
	party	     = fields.Many2one('res.partner')
	hawala_ref	     = fields.Many2one('res.partner',string = "Hawala Ref")
	rate			 = fields.Float()
	qty		 = fields.Float()
	settled_quantity		 = fields.Float(string="Settled Quantity")
	set_rate = fields.Float(string="Settled Rate")
	adjustment		 = fields.Many2many('contract.adjustments')
	remaining		 = fields.Float()

	forward_contract_id = fields.Many2one('forward.contract')


class ContractSettlementSummary(models.Model):

	_name 		 = 'contract.settlement.summary'
	_description = 'Tree View of Contract Settlement Summary'





	date = fields.Date()
	number = fields.Char()
	types                  = fields.Selection([
		('sale', 'Sale'),
		('purchase', 'Purchase'),
		],string = "Type")
	party	     = fields.Many2one('res.partner')
	rate			 = fields.Float()
	qty		 = fields.Float()
	settled_quantity		 = fields.Float(string="Settled Quantity")
	set_rate = fields.Float(string="Settled Rate")
	adjustment		 = fields.Many2many('contract.adjustments')
	remaining		 = fields.Float()

	forward_contract_id = fields.Many2one('forward.contract')



class Hawala(models.Model): 
	_name 		 = 'hawala' 
	_description = 'Hawala'
	_rec_name = 'date'
	
	date =  fields.Date(string ="Work Date")
	

	hawala_lines	 =	fields.One2many('hawala.lines','hawala_id' )


	@api.one
	@api.constrains('date')
	def single_date(self):

		dates = self.env['hawala'].search([('date','=',self.date),('id','!=',self.id)])
		if dates:
			raise ValidationError('Date Already Exists')


	@api.onchange('date')
	def change_date(self):
		for x in self.hawala_lines:
			x.date = self.date



class HawalaLines(models.Model): 
	_name 		 = 'hawala.lines' 
	_description = 'Hawala'

	
	date = fields.Date(default=fields.Date.context_today)
	mill = fields.Many2one('product.product')
	from_party = fields.Many2one('res.partner',string = "From")
	to = fields.Many2one('res.partner')
	maturity_date = fields.Date()
	rate = fields.Float()
	qty = fields.Float()
	amount = fields.Float(compute = "get_amount",store = True)


	hawala_id	 =	fields.Many2one('hawala' ,string = "Work Date", required = True)

	@api.onchange('mill','hawala_id')
	def get_date(self):
		self.date = self.hawala_id.date



	@api.one
	@api.depends('rate','qty')
	def get_amount(self):
		self.amount = self.rate * self.qty

	@api.model
	def create(self, vals):

		new_record = super(HawalaLines, self).create(vals)

		contract_sale = self.env['forward.contract'].search([('maturity_date','=',new_record.maturity_date),('mill','=',new_record.mill.id),('party','=',new_record.to.id)])
		contract_purchase = self.env['forward.contract'].search([('maturity_date','=',new_record.maturity_date),('mill','=',new_record.mill.id),('party','=',new_record.from_party.id)])
		if contract_sale and contract_purchase:
			for x in range(2):
				if x == 0:
					forward_contract_id = contract_sale.id
				elif x == 1:
					forward_contract_id = contract_purchase.id 
				create_contract_lines = self.env['forward.hawala'].search([]).create({
					'date': new_record.date,
					'from_party': new_record.from_party.id,
					'to':new_record.to.id,
					'rate':new_record.rate,
					'qty':new_record.qty,
					'amount':new_record.amount,
					'forward_contract_id':forward_contract_id,
					'hawala_id':new_record.id,
					})

		return new_record


	@api.multi
	def write(self, vals):
		super(HawalaLines, self).write(vals)

		relevant_hawala = self.env['forward.hawala'].search([('hawala_id','=',self.id)])
		for x in relevant_hawala:
			x.unlink()
		

		contract_sale = self.env['forward.contract'].search([('maturity_date','=',self.maturity_date),('mill','=',self.mill.id),('party','=',self.to.id)])
		contract_purchase = self.env['forward.contract'].search([('maturity_date','=',self.maturity_date),('mill','=',self.mill.id),('party','=',self.from_party.id)])
		if contract_sale and contract_purchase:
			for x in range(2):
				if x == 0:
					forward_contract_id = contract_sale.id
				elif x == 1:
					forward_contract_id = contract_purchase.id 
				create_contract_lines = self.env['forward.hawala'].search([]).create({
					'date': self.date,
					'from_party': self.from_party.id,
					'to':self.to.id,
					'rate':self.rate,
					'qty':self.qty,
					'amount':self.amount,
					'forward_contract_id':forward_contract_id,
					'hawala_id':self.id,
					})

		return True


	@api.multi
	def unlink(self):
		relevant_hawala = self.env['forward.hawala'].search([('hawala_id','=',self.id)])
		for x in relevant_hawala:
			x.unlink()
		super(HawalaLines, self).unlink()

		return True


class ContractAdjustements(models.Model): 
	_name 		 = 'contract.adjustments' 
	_description = 'Adjustments'
	_rec_name = 'number'

	
	number = fields.Char()
	qty = fields.Float()
	rate = fields.Float()
	settlement_id = fields.Integer()



class ContractTrial(models.Model): 
	_name 		 = 'contract.trial' 
	_description = 'Contract Trial'


	
	maturity_date = fields.Date()
	mill = fields.Many2one('product.product')
	total_sales = fields.Float(string = "Total Sales")
	total_purchase = fields.Float(string = "Total Purchases")
	net = fields.Float(string = "Available for Sale")


	trial_lines = fields.One2many('forward.contract','contract_trial_id')


	@api.multi
	def get_values(self):

		relevant_forwards = self.env['forward.contract'].search([('maturity_date','=',self.maturity_date),('mill','=',self.mill.id)])

		for x in relevant_forwards:
			x.create_settlement()
			x.contract_trial_id = self.id

		sales = 0
		purchase = 0
		for x in self.trial_lines:
			sales = sales + x.total_sales_qty
			purchase = purchase + x.total_purchase_qty

		self.total_sales = sales
		self.total_purchase = purchase
		self.net = self.total_purchase - self.total_sales

		










		