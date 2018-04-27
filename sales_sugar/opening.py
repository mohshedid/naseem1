# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
import datetime



class StockOpenings(models.Model): 
	_name 		 = 'stock.open' 
	_description = 'Stock Openning'
	_rec_name = 'date'


	date = fields.Date(required=True, default=fields.Date.context_today, string = "Opening Date")
	description = fields.Char(required=True,default = "Opening")
	
	stock_open_lines = fields.One2many('stock.open.line','opening_id')



	@api.multi
	def update_stock(self):
		# for x in self.stock_open_lines:

		relevant_summary = self.env['stock.summary.sugar'].search([])
		# if not relevant_summary:
		# 	raise ValidationError('Please create Product First')

		# else:
		relevant_summary.qty = 0


class StockOpeningLines(models.Model): 
	_name 		 = 'stock.open.line' 
	_description = 'Stock Openning Lines'
	# _rec_name = 'date'


	date = fields.Date()
	types                  = fields.Selection([
	('sale', 'Sale'),
	('purchase', 'Purchase'),
	],string = "Type",default = "sale" ,requried = True)
	mill = fields.Many2one('product.product',requried = True)
	party = fields.Many2one('res.partner',requried = True)
	qty = fields.Float(string ="Quantity")
	opening_id = fields.Many2one('stock.open')


	@api.model
	def create(self, vals):

		new_record = super(StockOpeningLines, self).create(vals)


		amanats = self.env['amanats'].search([('mill','=',new_record.mill.id),('customer','=',new_record.party.id)])
		if not amanats:
			create_amanat = amanats.create({
				'customer': new_record.party.id,
				'mill':new_record.mill.id 
				})
		amanats = self.env['amanats'].search([('mill','=',new_record.mill.id),('customer','=',new_record.party.id)])
		if new_record.types == "sale":
			amanats.sales = amanats.sales + new_record.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers
		if new_record.types == "purchase":
			amanats.purchases = amanats.purchases + new_record.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers
		


		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',new_record.mill.id)])
		if not relevant_summary:
			raise ValidationError('Please create Product First')

		else:
			if new_record.types == "purchase":
				relevant_summary.qty = relevant_summary.qty + new_record.qty
				relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat

			if new_record.types == "sale":
				relevant_summary.amanat = relevant_summary.amanat + new_record.qty
				relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat

		if new_record.party.mill == True and new_record.types == "purchase" :
			relevant_mill = self.env['mill.wise'].search([('mill','=',new_record.party.id),('brand','=',new_record.mill.id)])
			if not relevant_mill:
				raise ValidationError('Associate brand with the mill')
			else:
				relevant_mill.total_purchase = relevant_mill.total_purchase + new_record.qty
				relevant_mill.remaining = relevant_mill.total_purchase - relevant_mill.loaded


		return new_record

	@api.multi
	def write(self, vals):

		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.party.id)])
		if self.types == "sale":
			amanats.sales = amanats.sales - self.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers
		if self.types == "purchase":
			amanats.purchases = amanats.purchases - self.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers

		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		if self.types == "purchase":
			relevant_summary.qty = relevant_summary.qty - self.qty
			relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat
		if self.types == "sale":
			relevant_summary.amanat = relevant_summary.amanat - self.qty
			relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat

		if self.party.mill == True and self.types == "purchase":
			relevant_mill = self.env['mill.wise'].search([('mill','=',self.party.id),('brand','=',self.mill.id)])
			relevant_mill.total_purchase = relevant_mill.total_purchase - self.qty
			relevant_mill.remaining = relevant_mill.total_purchase - relevant_mill.loaded			



		super(StockOpeningLines, self).write(vals)

		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.party.id)])
		if not amanats:
			create_amanat = amanats.create({
				'customer': self.party.id,
				'mill':self.mill.id 
				})
		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.party.id)])
		if self.types == "sale":
			amanats.sales = amanats.sales + self.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers
		if self.types == "purchase":
			amanats.purchases = amanats.purchases + self.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers

		

		if self.party.mill == True and self.types == "purchase":
			relevant_mill = self.env['mill.wise'].search([('mill','=',self.party.id),('brand','=',self.mill.id)])
			if not relevant_mill:
				raise ValidationError('Associate brand with the mill')
			else:
				relevant_mill.total_purchase = relevant_mill.total_purchase + self.qty
				relevant_mill.remaining = relevant_mill.total_purchase - relevant_mill.loaded

		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		if not relevant_summary:
			raise ValidationError('Please create Product First')
		else:
			if self.types == "purchase":
				relevant_summary.qty = relevant_summary.qty + self.qty
				relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat
			if self.types == "sale":
				relevant_summary.amanat = relevant_summary.amanat + self.qty
				relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat			
		
		return True

	@api.multi
	def unlink(self):

		amanats = self.env['amanats'].search([('mill','=',self.mill.id),('customer','=',self.party.id)])
		if self.types == "sale":
			amanats.sales = amanats.sales - self.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers
		if self.types == "purchase":
			amanats.purchases = amanats.purchases - self.qty
			amanats.amanat = (amanats.sales - amanats.purchases) - (amanats.delivered - amanats.received) + amanats.amanat_transfers

		

		if self.party.mill == True and self.types == "purchase":
			relevant_mill = self.env['mill.wise'].search([('mill','=',self.party.id),('brand','=',self.mill.id)])
			relevant_mill.total_purchase = relevant_mill.total_purchase - self.qty
			relevant_mill.remaining = relevant_mill.total_purchase - relevant_mill.loaded

		relevant_summary = self.env['stock.summary.sugar'].search([('mill','=',self.mill.id)])
		if self.types =="purchase":
			relevant_summary.qty = relevant_summary.qty - self.qty	
			relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat
		if self.types == "sale":
			relevant_summary.amanat = relevant_summary.amanat - self.qty
			relevant_summary.for_sale = relevant_summary.qty - relevant_summary.amanat			
		
		super(StockOpeningLines, self).unlink()

		

		return True



