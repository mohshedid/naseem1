# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta , date
from odoo.exceptions import Warning, ValidationError

class CustomerFromVinsoft(models.Model):
	_inherit = 'res.partner'

	rut = fields.Char(string="Rut",index=True)
	name = fields.Char(string="Razón Social",required=False,default=" ")
	commerical_business = fields.Many2one('sii.activity.description',string="Giro Comercial")
	comuna = fields.Char(string="Comuna")
	mail_dte = fields.Char(string="Mail Recepción DTE")
	others = fields.Boolean(string='Otros')
	property_account_receivable_id = fields.Many2one('account.account',string="Cuenta para Ventas",required=False)
	document_type_id = fields.Many2one('sii.document_type',string="Document Type")
	responsability_id = fields.Many2one('sii.responsability',string="Responsability")
	property_payment_term_id = fields.Many2one('account.payment.term',string="Condiciones de Venta")
	property_product_pricelist = fields.Many2one('product.pricelist',string="Listado de Precios Asociada")
	contact_address = fields.One2many('address.contacts','address_contact_id')
	customer_sales = fields.One2many('sale.order', 'partner_onchange',readonly=True)
	customer_invoice = fields.One2many('account.invoice', 'partner_onchange',readonly=True)
	invoice_date_from = fields.Date(string="Fecha Desde")
	invoice_date_to = fields.Date(string="Fecha Hasta")
	sale_date_from = fields.Date(string="Fecha Desde")
	sale_date_to = fields.Date(string="Fecha Hasta")
	state = fields.Selection([
		('active','Activo'),
		('inactive','Inactivo'),
		],string='Estado',default='active')
	sale_state = fields.Selection([
		('draft', 'Quotation'),
		('sent', 'Quotation Sent'),
		('sale', 'Sale Order'),
		('done', 'Locked'),
		('cancel','Cancelled'),], string='Tipo')
	sale_name = fields.Char(string="Número")
	sale_date_order = fields.Date(string="Fecha Emisión")
	sale_amount_total = fields.Float(string="Monto")
	invoice_date_from = fields.Date(string="Fecha Desde")
	invoice_date_to = fields.Date(string="Fecha Hasta")
	invoice_state = fields.Selection([
		('draft', 'Draft'),
		('open', 'Open'),
		('paid', 'Paid'),
		('cancel','Cancelled'),], string='Tipo')
	invoice_number = fields.Char(string="Número")
	invoice_date_invoice = fields.Date(string="Fecha Emisión")
	invoice_amount_total = fields.Float(string="Slado")
	invoice_residual = fields.Float(string="Monto")
	active = fields.Boolean(string="active", default=True)


	@api.model
	def create(self, vals):

		new_record = super(CustomerFromVinsoft, self).create(vals)
		if new_record.rut:
			if len(new_record.rut) != 9:
				raise  ValidationError('Enter Proper Value In Rut')
			else:
				fst = new_record.rut[:2]
				scnd = new_record.rut[2:5]
				third = new_record.rut[5:8]
				forth = new_record.rut[-1]
				new_record.rut = fst + "." + scnd + "." + third + "-" + forth
			if new_record.name != " ":
				ruth_entries = self.env['ruth']
				ruth_id = ruth_entries.create({
						'name': new_record.id,
						'number': new_record.rut,
						'rec_new_name':new_record.name + " " + new_record.rut,
					})

		return new_record


	@api.multi
	def write(self, vals):
		res = super(CustomerFromVinsoft, self).write(vals)
		if self.rut:
			if len(self.rut) != 12 or self.rut[-2] != "-" or self.rut[-6] != "." or self.rut[-10] != ".":
				raise  ValidationError('Enter Proper Value In Rut')
		if self.sale_date_from and self.sale_date_to:
			rec = self.env['sale.order'].search([('partner_id','=',self.id)])
			for z in rec:
				z.partner_onchange = z.partner_id.id
		if self.invoice_date_from and self.invoice_date_to:
			records = self.env['account.invoice'].search([('partner_id','=',self.id)])
			for x in records:
				x.partner_onchange = x.partner_id.id
		rut_rec = self.env['ruth'].search([('name.id','=',self.id)])
		if rut_rec:
			rut_rec.number = self.rut
			rut_rec.name = self.id
			rut_rec.rec_new_name = self.name + " " + self.rut

		return res


	@api.onchange('state')
	def get_active(self):
		if self.state == "inactive":
			self.active = False
		else:
			self.active = True


	@api.onchange('name')
	def get_doc(self):
		records = self.env['sii.document_type'].search([('name','=',"RUT")])
		self.document_type_id = records.id
		rec = self.env['sii.responsability'].search([('name','=',"IVA Afecto / 1ra Categoría")])
		self.responsability_id = rec.id



	@api.multi
	def customer_search(self):
		return {'name': 'Search Customer',
				'domain': [],
				'res_model': 'customer.search',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'view_type': 'form',
				'target': 'new', 
				}




# ===============================================onchange serach for sales =======================================
# ===============================================onchange serach for sales =======================================
# ===============================================onchange serach for sales =======================================



	
	@api.onchange('sale_state','sale_name','sale_date_order','sale_amount_total')
	def get_sale_data(self):
		tree_rec = []
		record = []
		if self.sale_state:
			state_str = str(self.sale_state)
		else:
			state_str = "none"
		if self.sale_name:
			name_str = str(self.sale_name)
		else:
			name_str = "none"
		if self.sale_date_order:
			date_str = str(self.sale_date_order)
		else:
			date_str = "none"
		if self.sale_amount_total:
			amount_str = str(self.sale_amount_total)
		else:
			amount_str = "none"
		search_text = state_str + name_str + date_str + amount_str
		rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
		for records in rec:
			if self.sale_state:
				state_rec = str(records.state)
			else:
				state_rec = "none"
			if self.sale_name:
				name_rec = str(records.name)
			else:
				name_rec = "none"
			if self.sale_date_order:
				date_rec = str(records.date_order[:10])
			else:
				date_rec = "none"
			if self.sale_amount_total:
				amount_rec = str(records.amount_total)
			else:
				amount_rec = "none"
			string = state_rec + name_rec + date_rec + amount_rec
			if search_text == string:
				tree_rec.append(records)
				
		for z in tree_rec:
			record.append({
				'state':z.state,
				'name':z.name,
				'date_order':z.date_order,
				'amount_total':z.amount_total,
				'partner_onchange':self._origin.id,
				})

		self.customer_sales = record


# ===============================================onchange serach for invoices =======================================
# ===============================================onchange serach for invoices =======================================
# ===============================================onchange serach for invoices =======================================


	@api.onchange('invoice_state','invoice_number','invoice_date_invoice','invoice_amount_total','invoice_residual')
	def get_invoice_data(self):
		tree_rec = []
		record = []
		if self.invoice_state:
			state_str = str(self.invoice_state)
		else:
			state_str = "none"
		if self.invoice_number:
			name_str = str(self.invoice_number)
		else:
			name_str = "none"
		if self.invoice_date_invoice:
			date_str = str(self.invoice_date_invoice)
		else:
			date_str = "none"
		if self.invoice_residual:
			residual_str = str(self.invoice_residual)
		else:
			residual_str = "none"
		if self.invoice_amount_total:
			amount_str = str(self.invoice_amount_total)
		else:
			amount_str = "none"
		search_text = state_str + name_str + date_str + amount_str + residual_str
		rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id)])
		for records in rec:
			if self.invoice_state:
				state_rec = str(records.state)
			else:
				state_rec = "none"
			if self.invoice_number:
				name_rec = str(records.number)
			else:
				name_rec = "none"
			if self.invoice_date_invoice:
				date_rec = str(records.date_invoice)
			else:
				date_rec = "none"
			if self.invoice_amount_total:
				amount_rec = str(records.amount_total)
			else:
				amount_rec = "none"
			if self.invoice_residual:
				residual_rec = str(records.residual)
			else:
				residual_rec = "none"
			string = state_rec + name_rec + date_rec + amount_rec + residual_rec
			if search_text == string:
				tree_rec.append(records)
				
		for z in tree_rec:
			record.append({
				'state':z.state,
				'number':z.number,
				'date_invoice':z.date_invoice,
				'residual':z.residual,
				'amount_total':z.amount_total,
				'partner_onchange':self._origin.id,
				})

		self.customer_invoice = record



		# ===========================================================================================================
		# ===========================================================================================================
		# ===========================================================================================================



	@api.multi
	def sale_search(self):
		if self.sale_date_from and self.sale_date_to:
			for x in self.customer_sales:
				x.partner_onchange = False
			rec = self.env['sale.order'].search([('partner_id','=',self.id)])
			for z in rec:
				if str(z.date_order[:10]) >= self.sale_date_from and str(z.date_order[:10]) <= self.sale_date_to:
					z.partner_onchange = self.id


	@api.multi
	def invoice_search(self):
		if self.invoice_date_from and self.invoice_date_to:
			for x in self.customer_invoice:
				x.partner_onchange = False
			rec = self.env['account.invoice'].search([('partner_id','=',self.id)])
			for z in rec:
				if z.date_invoice >= self.invoice_date_from and z.date_invoice <= self.invoice_date_to:
					z.partner_onchange = self.id





class SaleFromVinsoft(models.Model):
	_inherit = 'sale.order'


	partner_onchange = fields.Many2one('res.partner')

	@api.onchange('partner_id')
	def get_partner(self):
		if self.partner_id:
			self.partner_onchange = self.partner_id.id



class InvoiceFromVinsoft(models.Model):
	_inherit = 'account.invoice'


	partner_onchange = fields.Many2one('res.partner')

	@api.onchange('partner_id')
	def get_partner(self):
		if self.partner_id:
			self.partner_onchange = self.partner_id.id


class EcubeCustomer(models.Model):
	_name = 'customer.search'


	name = fields.Many2one('res.partner',string="Customers")
	rut = fields.Many2one('ruth',string="Rut")


	@api.onchange('rut')
	def get_name(self):
		if self.rut:
			self.name = self.rut.name.id


	@api.onchange('name')
	def get_rut(self):
		if self.name:
			rut_rec = self.env['ruth'].search([('name.id','=',self.name.id)])
			if rut_rec:
				self.rut = rut_rec.id
			else:
				self.rut = False


	@api.multi
	def get_customer(self):
		rec = self.env['res.partner'].search([('id','=',self.name.id)]).id
		view_id = self.env.ref('vinsoft_customer.vinsoft_customer_form_view').id
		active_id = self.env.context.get('active_id')
		records = self.env['res.partner'].search([('id','=',active_id)])
		if records.name == " ":
			records.unlink()
		return {
				'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'view_id' : view_id,
                'target': 'main',
                'res_id': rec,
				}



class DocumentEcube(models.Model):
	_name = 'sii.document_type'

	name = fields.Char()


class ResponseEcube(models.Model):
	_name = 'sii.responsability'

	name = fields.Char()


class RuthEcube(models.Model):
	_name = 'ruth'
	_rec_name = 'rec_new_name'

	number = fields.Char()
	rec_new_name = fields.Char()
	name = fields.Many2one('res.partner',string="Name")







	



