# -*- coding: utf-8 -*-
from odoo import models, fields, api
import random

class taxes_champion(models.Model):
	_inherit = 'account.tax'

	type_tax_use = fields.Selection([ ('sale', 'Sales'), ('purchase', 'Purchases'), ('none', 'None'), ('payment', 'Payment'), ('receipt', 'Receipt'), ('salary', 'Salary'),])
	tax_nautre = fields.Selection([ ('cd', 'Customs Duty'),('acd', 'Additional Customs Duty'), ('st', 'Sales Tax'), ('ast', 'Additional Sales Tax'), ('it', 'Income Tax')])

	amount_type = fields.Selection([('group', 'Group of Taxes'), ('fixed', 'Fixed'), ('percent', 'Percentage of Price'), ('division', 'Percentage of Price Tax Included') ])

	cp_sales_type = fields.Many2one('sales.type.bcube','Sales Type')
	cp_sro_no = fields.Many2one('sro.schno.bcube','SRO No. /Schedule No')
	cp_item_sr_no = fields.Many2one('item.srno.bcube','Item Sr. No')
	cp_item_desc = fields.Many2one('item.desc.bcube','Description')
	fbr_tax_code = fields.Char(string="FBR Tax Code")
	enable_child_tax = fields.Boolean('Tax on Children')

class SalesTypeBcube(models.Model):
	_name = 'sales.type.bcube'
	name = fields.Char('Name')

class ItemSrnoBcube(models.Model):
	_name = 'item.srno.bcube'
	name = fields.Char('Name')

class SroSchnoBcube(models.Model):
	_name = 'sro.schno.bcube'
	name = fields.Char('Name')

class ItemDescBcube(models.Model):
	_name = 'item.desc.bcube'
	name = fields.Char('Name')

class OtherCostTree(models.Model):
	_name ="other.cost.tree"

	date = fields.Date(string="Date")
	expense_type = fields.Many2one('other.costs.type',string="Expense Type")
	vendor = fields.Many2one('res.partner',string="Vendor Name")
	bank = fields.Many2one('account.journal', string="Bank")
	reference = fields.Char(string="Reference")
	amount = fields.Float(string="Amount")
	tree_link = fields.Many2one('account.invoice', string="Tree Link")

class AccountInvoiceBcube(models.Model):
	_inherit = 'account.invoice'

	date_invoice = fields.Date(string="Invoice Date", required=True, readonly=False, select=True, default=lambda self: fields.date.today())
	others_tree = fields.One2many('other.cost.tree','tree_link')
	import_tree = fields.One2many('sales.invoice.tree','tree_link')
	gd_no = fields.Char(string = "GD No")
	dollar_rate = fields.Float(string = "Dollar Rate")


	@api.multi
	def calculate_costs(self):
		total_costs = 0
		for x in self.others_tree:
			total_costs = total_costs + x.amount

		total_value = 0
		for x in self.invoice_line_ids:
			total_value = total_value + x.price_unit

		for x in self.invoice_line_ids:
			ratio = x.price_unit/total_value
			x.per_unit_cost = (ratio * total_costs) + (x.bcube_amount_tax/x.quantity) + x.price_unit
	

	@api.one
	def _compute_amount(self):
		res = super(AccountInvoiceBcube, self)._compute_amount()
		self.amount_tax = sum(line.amount for line in self.tax_line_ids)
		self.amount_total = self.amount_untaxed + self.amount_tax
		return res


	@api.onchange('dollar_rate')
	def change_dollar(self):
		for x in self.invoice_line_ids:
			x.assessed = self.dollar_rate * x.assessed_dollar
			x.price_unit = self.dollar_rate * x.declared_dollar

	@api.multi
	def generate_lines(self):
		remaining = 0
		for x in self.import_tree:
			product_price = x.product_id.list_price
			product_quant = int(x.price_subtotal/product_price)


			create_invoice_line = self.env['account.invoice.line'].create({
				'product_id': x.product_id.id,
				'name': x.descrip,
				'account_id': x.account.id,
				'quantity': product_quant,
				'price_unit': product_price,
				# 'bcube_taxes_id': x.line_taxes,
				# 'amount_subtoal': counted_price,
				'invoice_id': self.id,
				
				})
		
		invoice_lines_amount = 0
		imported_lines_amount = 0

		for amount in self.invoice_line_ids:
			invoice_lines_amount = invoice_lines_amount + (amount.quantity * amount.price_unit)
		for imp_amount in self.import_tree:
			imported_lines_amount = imported_lines_amount + imp_amount.price_subtotal
		
		limit = imported_lines_amount - invoice_lines_amount
		print limit
		while limit > 0:
			products = self.env['product.template'].search([('list_price','<',limit)])
			if products:
				random_product = random.choice(products)
				create_invoice_line = self.env['account.invoice.line'].create({
						'product_id': random_product.id,
						'name': random_product.name,
						'account_id': random_product.property_account_income_id.id,
						'quantity': 1,
						'price_unit': random_product.list_price,
						# 'amount_subtoal': int(e.list_price * prod_quant),
						'invoice_id': self.id,
						
						})
				limit = limit - random_product.list_price
			else:
				products = self.env['product.template'].search([])
				prices = []
				for x in products:
					prices.append(x.list_price)
				final_price = min(prices, key=lambda x:abs(x-limit))
				final_product = self.env['product.template'].search([('list_price','=',final_price)])
				create_invoice_line = self.env['account.invoice.line'].create({
						'product_id': final_product.id,
						'name': final_product.name,
						'account_id': final_product.property_account_income_id.id,
						'quantity': 1,
						'price_unit': limit,
						# 'amount_subtoal': int(e.list_price * prod_quant),
						'invoice_id': self.id,
						
						})
				limit = 0


		line_data = self.env['account.invoice.line'].search([('invoice_id','=',self.id)])
		for a in line_data:
			a.bcube_taxes_id = a.product_id.taxes_id



		# tax_lines = self.env['account.invoice.tax'].search([])
		# tax_line_tree = []
		# for x in self.invoice_line_ids:
		# 	for y in x.bcube_taxes_id:
		# 		if y.id not in tax_line_tree:
		# 			tax_line_tree.append(y.id)

		# for taxes in self.invoice_line_ids:
		# 	for tax in taxes.bcube_taxes_id:
		# 		if tax.id not in taxes:
		# 			taxes.append(tax.id)
		# for ids in tax_line_tree:
		# 	tax_lines = self.env['account.tax'].search([('id','=',ids)])
		# 	print tax_lines.name
		# 	tax_lines.create({
		# 		'name': tax_lines.name,
		# 		'account_id': tax_lines.account_id.id,
		# 		'invoice_id': self.id,
		# 		'tax_id': tax_lines.id,
		# 		'amount': 0,
		# 		})



		# 	a.bcube_amount_tax = self.invoice_line_ids.calculateTaxAmount(a.bcube_taxes_id,a.quantity,unit_price)
		# 	a.amount_subtoal = (a.quantity * a.price_unit) + a.bcube_amount_tax



		



	@api.onchange('invoice_line_ids')
	def _onchange_invoice_line_ids(self):
		# if self.type == 'in_invoice':
		res = super(AccountInvoiceBcube, self)._onchange_invoice_line_ids()
		self.tax_line_ids = 0
		records = []
		taxes_ids = []
		for taxes in self.invoice_line_ids:
			for tax in taxes.bcube_taxes_id:
				if tax.id not in taxes_ids:
					taxes_ids.append(tax.id)
					
					records.append({
						'name':tax.name,
						'account_id':taxes.account_id.id,
						'invoice_id':self.id,
						'tax_id':tax.id,
						'amount': 0,
						})
				
			self.tax_line_ids = records
		for taxes in self.invoice_line_ids:

			for tax in taxes.bcube_taxes_id:
				
				if self.type == 'in_invoice':
					unit_price = taxes.assessed -(taxes.assessed * (taxes.discount/100) )
				
				if self.type == 'out_invoice':
					unit_price = taxes.price_unit -(taxes.price_unit * (taxes.discount/100) )



				amount_tax = self.invoice_line_ids.calculateTaxAmount(taxes,tax,taxes.quantity,unit_price)
				if self.tax_line_ids:
					for line in self.tax_line_ids:
						if line.name == tax.name:
							line.amount = line.amount + amount_tax

		return res



	@api.multi
	def validator(self):
		seq = self.env['ir.sequence'].search([('name','=','Vendor Bills')])
		seq.code = 'vendor.bills.seq'
		self.number = self.env['ir.sequence'].next_by_code('vendor.bills.seq')
		create_move = self.env['account.move'].create({
			'journal_id':self.journal_id.id,
			'date':self.date_invoice,
			'ref':self.number

		})

		create_move_line = self.env['account.move.line'].create({
			'account_id': self.journal_id.default_debit_account_id.id,
			'name': 'name',
			'move_id': create_move.id,
			'date_maturity': self.date_invoice,
			'partner_id': self.partner_id.id,
			'debit': self.amount_untaxed
		})

		create_move_line = self.env['account.move.line'].create({
			'account_id': self.partner_id.property_account_payable_id.id,
			'name': 'name2',
			'move_id': create_move.id,
			'date_maturity': self.date_invoice,
			'partner_id': self.partner_id.id,
			'credit': self.amount_untaxed
		})

		for x in self.tax_line_ids:

			create_move_line = self.env['account.move.line'].create({
				'account_id': x.account_id.id,
				'name': 'name',
				'move_id': create_move.id,
				'date_maturity': self.date_invoice,
				# 'partner_id': self.partner_id.id,
				'debit': x.amount
			})

			create_move_line = self.env['account.move.line'].create({
				'account_id': x.tax_id.counter_tax.id,
				'name': 'name2',
				'move_id': create_move.id,
				'date_maturity': self.date_invoice,
				# 'partner_id': self.partner_id.id,
				'credit': x.amount
			})

		inventory = self.env['stock.picking']
		inventory_lines = self.env['stock.move'].search([])
		create_inventory = inventory.create({
			'partner_id':self.partner_id.id,
			'location_id':15,
			'picking_type_id' : 1,
			'location_dest_id' : 9,
			'origin':self.name,

		})


		for x in self.invoice_line_ids:
			create_inventory_lines= inventory_lines.create({
				'product_id':x.product_id.id,
				# 'product_uom_qty':x.product_uom_qty,
				'product_uom': x.product_id.uom_id.id,
				'location_id':15,
				'picking_id': create_inventory.id,
				'name':"test",
				'location_dest_id': 9,
				})
		# create_inventory.action_assign()
		return self.write({'state':'draft'})




class AccountMoveRemoveValidation(models.Model):
	_inherit = "account.move"


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

class AccountInvoiceLineBcube(models.Model):
	_inherit = 'account.invoice.line'

	bcube_taxes_id = fields.Many2many('account.tax',
		'account_invoice_line_tax', 'invoice_line_id', 'tax_id',
		string='Taxes', domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)], oldname='invoice_line_tax_id')
	bcube_amount_tax = fields.Float(string = "Tax Included")

	assessed = fields.Float(string="Assessed")
	per_unit_cost = fields.Float(string="Per Unit Cost")
	tax_Amount = fields.Float(string="Tax Amount")
	assessed_dollar = fields.Float(string="Ass $")
	declared_dollar = fields.Float(string="Declared $")


	line_taxes = fields.Many2many('account.tax',string="Taxes")

	amount_subtoal = fields.Float(string="Amount")


	@api.onchange('bcube_taxes_id','price_unit','quantity','discount','assessed')
	def onChBcubeTaxes(self):

		if self.invoice_id.type == 'out_invoice':
			unit_price = self.price_unit -(self.price_unit * (self.discount/100) )
		
		if self.invoice_id.type == 'in_invoice':
			unit_price = self.assessed -(self.assessed * (self.discount/100) )


		self.bcube_amount_tax = self.calculateTaxAmountInc(self.bcube_taxes_id, self.quantity, unit_price)

	@api.onchange('assessed_dollar','declared_dollar')
	def get_pak_rupee(self):

		self.assessed = self.invoice_id.dollar_rate * self.assessed_dollar
		self.price_unit = self.invoice_id.dollar_rate * self.declared_dollar


	@api.onchange('product_id')
	def getProductTaxes(self):
		all_taxes = []
		for x in self.product_id.supplier_taxes_id:
			all_taxes.append((4,x.id))

		self.bcube_taxes_id = all_taxes
		self.discount = self.invoice_id.partner_id.discount
		
	def calculateTaxAmount(self, taxes_lines,taxes, qty, price_unit):
		custom_duty = 0
		acd_duty = 0
		income_tax = 0
		sale_tax=0
		add_tax = 0
		for x in taxes_lines.bcube_taxes_id:
			# print x.name
			if x.tax_nautre == "cd":
				custom_duty = custom_duty +  (x.amount/100)
			if x.tax_nautre == "acd":
				acd_duty = acd_duty +  (x.amount/100)
			if x.tax_nautre == "it":
				income_tax = income_tax + (x.amount/100)
			if x.tax_nautre == "st":
				sale_tax = sale_tax + (x.amount/100)
			if x.tax_nautre == "ast":
				add_tax = add_tax + (x.amount/100)

		total_cd = custom_duty + acd_duty



		amount_tax = 0
		rate = 0
		for tax in taxes:
			if tax.tax_nautre == "cd":
				rate = custom_duty
			if tax.tax_nautre == "acd":
				rate = acd_duty
			if tax.tax_nautre == "st":
				rate = (sale_tax) + (sale_tax * total_cd)
			if tax.tax_nautre == "ast":
				rate = (add_tax) + (add_tax * total_cd)
			if tax.tax_nautre == "it":
				rate = income_tax + (income_tax * ((sale_tax) + (sale_tax * total_cd)) + (income_tax * total_cd)) + (income_tax * ((add_tax) + (add_tax * total_cd)))

			# print tax.tax_nautre
			# print rate
			

			# amount_tax = amount_tax + qty * price_unit * (rate/100)
		 

			# if "CD" in tax.name:
			# if tax.enable_child_tax:
			# 	if tax.children_tax_ids:
			# 		child_tax = 0
			# 		for childtax in tax.children_tax_ids:
			# 			child_amount_tax = qty * price_unit * (childtax.amount/100) * (tax.amount/100)
		
			# 			child_tax = child_tax + child_amount_tax 
			# 		parent_tax = qty * price_unit * (tax.amount /100)
			# 		child_tax_final = child_tax + parent_tax
			# 		amount_tax += child_tax_final

			# else:
			# if tax.effective_rate == 0:
			# 	rate = tax.amount
			# else:
			# 	rate = tax.effective_rate
			amount_tax += qty * price_unit * (rate)
		
		return amount_tax


	def calculateTaxAmountInc(self, taxes, qty, price_unit):
		amount_tax = 0
		child_tax = 0
		child_tax_final=0
		for tax in taxes:
			# if tax.enable_child_tax:
			# 	if tax.children_tax_ids:
			# 		child_tax = 0
			# 		for childtax in tax.children_tax_ids:
			# 			child_amount_tax = qty * price_unit * (childtax.amount/100) * (tax.amount/100)
		
			# 			child_tax = child_tax + child_amount_tax 
			# 		parent_tax = qty * price_unit * (tax.amount /100)
			# 		child_tax_final = child_tax + parent_tax
			# 		amount_tax += child_tax_final

			# else:
			if tax.cost_included == True:
				if tax.effective_rate == 0:
					rate = tax.amount
				else:
					rate = tax.effective_rate
				amount_tax += qty * price_unit * (rate /100)
		
		return amount_tax

class DiscountAmount(models.Model):
	_inherit  = 'res.partner'
	discount = fields.Float(string="Discount%")

class SalesInvoiceExtension(models.Model):
	_name = 'sales.invoice.tree'
	_rec_name = 'product_id'

	product_id = fields.Many2one('product.product',string="Product")
	account = fields.Many2one('account.account',string="Account")
	tree_link = fields.Many2one('account.invoice')

	quantity = fields.Float(string="Quantity")
	unit_price = fields.Float(string="Unit Price")
	tax_amount = fields.Float(string="Amount Tax")
	price_subtotal = fields.Float(string="Amount")

	line_taxes = fields.Many2many('account.tax',string="Taxes")

	descrip = fields.Text(string="Description")

	@api.onchange('product_id')
	def onchange_product_id(self):
		self.unit_price = self.product_id.list_price
		self.quantity = 1
		self.descrip = self.product_id.name
		self.line_taxes = self.product_id.taxes_id

	@api.onchange('quantity','unit_price')
	def onchange_quant(self):
		self.price_subtotal = self.quantity * self.unit_price

# class ImportInvoice_lines(models.Model):
# 	_inherit = 'account.invoice'

# 	import_tree = fields.One2many('sales.invoice.tree','tree_link')

class AccountTaxAmount(models.Model):
	_inherit = 'account.tax'

	counter_tax = fields.Many2one('account.account',string="Counter Tax")
	effective_rate = fields.Float(string="Effective Rate",digits=(12,6))
	cost_included = fields.Boolean(string = "Cost Included")


	@api.onchange('children_tax_ids')
	def get_effective_rate(self):
		total_child = 0
		for x in self.children_tax_ids:
			if x.effective_rate == 0:
				effective_rate = x.amount
			else:
				effective_rate = x.effective_rate
			total_child = total_child +  effective_rate

		print total_child

		self.effective_rate = ((100 + total_child) * (self.amount/100))



class OtherCostsType(models.Model):
	_name = 'other.costs.type'

	name = fields.Char()
	associated_account = fields.Many2one('account.account')
