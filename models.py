# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta , date

class CustomerFromVinsoft(models.Model):
	_inherit = 'res.partner'

	rut = fields.Char(string="Rut",readonly=True,index=True)
	name = fields.Char(string="Razón Social",required=True)
	commerical_business = fields.Char(string="Giro Comercial")
	comuna = fields.Char(string="Comuna")
	mail_dte = fields.Char(string="Mail Recepción DTE")
	others = fields.Boolean(string='Otros')
	property_account_receivable_id = fields.Many2one('account.account',string="Cuenta para Ventas")
	document_type_id = fields.Many2one('sii.document_type',string="Document Type")
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
		vals['rut'] = self.env['ir.sequence'].next_by_code('customer.seq')
		new_record = super(CustomerFromVinsoft, self).create(vals)
		

		return new_record


	@api.multi
	def write(self, vals):
		res = super(CustomerFromVinsoft, self).write(vals)
		if self.sale_date_from and self.sale_date_to:
			rec = self.env['sale.order'].search([('partner_id','=',self.id)])
			for z in rec:
				z.partner_onchange = z.partner_id.id
		if self.invoice_date_from and self.invoice_date_to:
			records = self.env['account.invoice'].search([('partner_id','=',self.id)])
			for x in records:
				x.partner_onchange = x.partner_id.id

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



	@api.onchange('sale_state')
	def get_tree_state(self):
		if self.sale_state:
			tree_rec = []
			records = []
			if self.sale_state and self.sale_date_order == False and self.sale_name == False and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id),('state','=',self.sale_state)])
				for x in rec:
					tree_rec.append(x)

			if self.sale_state and self.sale_date_order and self.sale_name == False and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order:
						tree_rec.append(x)

			if self.sale_state and self.sale_date_order and self.sale_name and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name:
						tree_rec.append(x)

			if self.sale_state and self.sale_date_order and self.sale_name  and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_state and self.sale_date_order == False and self.sale_name and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and x.name == self.sale_name:
						tree_rec.append(x)

			if self.sale_state and self.sale_date_order == False and self.sale_name == False and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_state and self.sale_date_order and self.sale_name == False and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_state and self.sale_date_order == False and self.sale_name and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)


			for z in tree_rec:
				records.append({
					'state':z.state,
					'name':z.name,
					'date_order':z.date_order,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})


			self.customer_sales = records
		if not self.sale_state:
			self.sale_name = False
			self.sale_amount_total = False
			self.sale_date_order = False
			new = []
			self.customer_sales = new



	@api.onchange('sale_date_order')
	def get_tree_date(self):
		if self.sale_date_order:
			tree_rec = []
			records = []
			if self.sale_date_order and self.sale_state == False and self.sale_name == False and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order:
						tree_rec.append(x)

			if self.sale_date_order and self.sale_state and self.sale_name == False and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order:
						tree_rec.append(x)

			if self.sale_date_order and self.sale_state and self.sale_name and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name:
						tree_rec.append(x)

			if self.sale_date_order and self.sale_state and self.sale_name  and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_date_order and self.sale_state == False and self.sale_name and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name:
						tree_rec.append(x)

			if self.sale_date_order and self.sale_state == False and self.sale_name == False and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_date_order and self.sale_state and self.sale_name == False and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_date_order and self.sale_state == False and self.sale_name and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)


			for z in tree_rec:
				records.append({
					'state':z.state,
					'name':z.name,
					'date_order':z.date_order,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_sales = records


	@api.onchange('sale_name')
	def get_tree_name(self):
		if self.sale_name:
			tree_rec = []
			records = []
			if self.sale_name and self.sale_state == False and self.sale_date_order == False and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id),('name','=',self.sale_name)])
				for x in rec:
					tree_rec.append(x)

			if self.sale_name and self.sale_state and self.sale_date_order == False and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and x.name == self.sale_name:
						tree_rec.append(x)

			if self.sale_name and self.sale_state and self.sale_date_order and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name:
						tree_rec.append(x)

			if self.sale_name and self.sale_state and self.sale_date_order  and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_name and self.sale_state == False and self.sale_date_order and self.sale_amount_total == 0.00:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name:
						tree_rec.append(x)

			if self.sale_name and self.sale_state == False and self.sale_date_order == False and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_name and self.sale_state and self.sale_date_order == False and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_name and self.sale_state == False and self.sale_date_order and self.sale_amount_total:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			for z in tree_rec:
				records.append({
					'state':z.state,
					'name':z.name,
					'date_order':z.date_order,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_sales = records


	@api.onchange('sale_amount_total')
	def get_tree_amt(self):
		if self.sale_amount_total:
			tree_rec = []
			records = []
			if self.sale_amount_total and self.sale_state == False and self.sale_date_order == False and self.sale_name == False:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id),('amount_total','=',self.sale_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.sale_amount_total and self.sale_state and self.sale_date_order == False and self.sale_name == False:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_amount_total and self.sale_state and self.sale_date_order and self.sale_name == False:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_amount_total and self.sale_state and self.sale_date_order  and self.sale_name:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_amount_total and self.sale_state == False and self.sale_date_order and self.sale_name == False:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_amount_total and self.sale_state == False and self.sale_date_order == False and self.sale_name:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_amount_total and self.sale_state and self.sale_date_order == False and self.sale_name:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if x.state == self.sale_state and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)

			if self.sale_amount_total and self.sale_state == False and self.sale_date_order and self.sale_name:
				rec = self.env['sale.order'].search([('partner_id','=',self._origin.id)])
				for x in rec:
					if str(x.date_order[:10]) == self.sale_date_order and x.name == self.sale_name and x.amount_total == self.sale_amount_total:
						tree_rec.append(x)
			

			for z in tree_rec:
				records.append({
					'state':z.state,
					'name':z.name,
					'date_order':z.date_order,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_sales = records


# ===============================================onchange serach for invoices =======================================
# ===============================================onchange serach for invoices =======================================
# ===============================================onchange serach for invoices =======================================

	@api.onchange('invoice_state')
	def get_inv_state(self):
		if self.invoice_state:
			tree_rec = []
			records = []
			if self.invoice_state and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_state and self.invoice_date_invoice and self.invoice_number == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_date_invoice == False and self.invoice_number == False and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_date_invoice == False and self.invoice_number == False and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number == False and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('residual','=',self.invoice_residual),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_state and self.invoice_number == False and self.invoice_date_invoice and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number == False and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			for z in tree_rec:
				records.append({
					'state':z.state,
					'number':z.number,
					'date_invoice':z.date_invoice,
					'residual':z.residual,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_invoice = records
		if not self.invoice_state:
			self.invoice_number = False
			self.invoice_date_invoice = False
			self.invoice_residual = False
			self.invoice_amount_total = False
			new = []
			self.customer_invoice = new



	@api.onchange('invoice_number')
	def get_inv_numb(self):
		if self.invoice_number:
			tree_rec = []
			records = []
			sale_ids = []
			if self.invoice_number and self.invoice_state == False and self.invoice_date_invoice == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state and self.invoice_date_invoice == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_number and self.invoice_date_invoice and self.invoice_state == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_date_invoice == False and self.invoice_state == False and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_date_invoice == False and self.invoice_state == False and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state and self.invoice_date_invoice and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state == False and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state == False and self.invoice_date_invoice == False and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_number and self.invoice_state and self.invoice_date_invoice == False and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_number and self.invoice_state == False and self.invoice_date_invoice and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state and self.invoice_date_invoice == False and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_number and self.invoice_state and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state and self.invoice_date_invoice and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state and self.invoice_date_invoice == False and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state == False and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_number and self.invoice_state and self.invoice_date_invoice and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			for z in tree_rec:
				records.append({
					'state':z.state,
					'number':z.number,
					'date_invoice':z.date_invoice,
					'residual':z.residual,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_invoice = records


	@api.onchange('invoice_date_invoice')
	def get_inv_date(self):
		if self.invoice_date_invoice:
			tree_rec = []
			records = []
			sale_ids = []
			if self.invoice_date_invoice and self.invoice_state == False and self.invoice_number == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state and self.invoice_number == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_date_invoice and self.invoice_number and self.invoice_state == False and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_number == False and self.invoice_state == False and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_number == False and self.invoice_state == False and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state and self.invoice_number and self.invoice_residual == 0.00 and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state == False and self.invoice_number and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state == False and self.invoice_number == False and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_date_invoice and self.invoice_state and self.invoice_number == False and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_date_invoice and self.invoice_state == False and self.invoice_number and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state and self.invoice_number == False and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_date_invoice and self.invoice_state and self.invoice_number and self.invoice_residual and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state and self.invoice_number and self.invoice_residual == 0.00 and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state and self.invoice_number == False and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state == False and self.invoice_number and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_date_invoice and self.invoice_state and self.invoice_number and self.invoice_residual and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			for z in tree_rec:
				records.append({
					'state':z.state,
					'number':z.number,
					'date_invoice':z.date_invoice,
					'residual':z.residual,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_invoice = records



	@api.onchange('invoice_residual')
	def get_inv_residual(self):
		if self.invoice_residual:
			tree_rec = []
			records = []
			sale_ids = []
			if self.invoice_residual and self.invoice_state == False and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_residual and self.invoice_number and self.invoice_state == False and self.invoice_date_invoice == False and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_number == False and self.invoice_state == False and self.invoice_date_invoice and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_number == False and self.invoice_state == False and self.invoice_date_invoice == False and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state == False and self.invoice_number and self.invoice_date_invoice and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state == False and self.invoice_number == False and self.invoice_date_invoice and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_residual and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_residual and self.invoice_state == False and self.invoice_number and self.invoice_date_invoice == False and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_residual and self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_amount_total == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state == False and self.invoice_number and self.invoice_date_invoice and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_residual and self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_amount_total:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			for z in tree_rec:
				records.append({
					'state':z.state,
					'number':z.number,
					'date_invoice':z.date_invoice,
					'residual':z.residual,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_invoice = records



	@api.onchange('invoice_amount_total')
	def get_inv_amt(self):
		if self.invoice_amount_total:
			tree_rec = []
			records = []
			sale_ids = []
			if self.invoice_amount_total and self.invoice_state == False and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_amount_total and self.invoice_number and self.invoice_state == False and self.invoice_date_invoice == False and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_number == False and self.invoice_state == False and self.invoice_date_invoice and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_number == False and self.invoice_state == False and self.invoice_date_invoice == False and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state == False and self.invoice_number and self.invoice_date_invoice and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('amount_total','=',self.invoice_amount_total),('date_invoice','=',self.invoice_date_invoice)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state == False and self.invoice_number == False and self.invoice_date_invoice and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_amount_total and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice == False and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_amount_total and self.invoice_state == False and self.invoice_number and self.invoice_date_invoice == False and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			if self.invoice_amount_total and self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_residual == 0.00:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state and self.invoice_number and self.invoice_date_invoice == False and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state and self.invoice_number == False and self.invoice_date_invoice and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state == False and self.invoice_number and self.invoice_date_invoice and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)

			if self.invoice_amount_total and self.invoice_state and self.invoice_number and self.invoice_date_invoice and self.invoice_residual:
				rec = self.env['account.invoice'].search([('partner_id','=',self._origin.id),('state','=',self.invoice_state),('number','=',self.invoice_number),('date_invoice','=',self.invoice_date_invoice),('residual','=',self.invoice_residual),('amount_total','=',self.invoice_amount_total)])
				for x in rec:
					tree_rec.append(x)


			for z in tree_rec:
				records.append({
					'state':z.state,
					'number':z.number,
					'date_invoice':z.date_invoice,
					'residual':z.residual,
					'amount_total':z.amount_total,
					'partner_onchange':self._origin.id,
					})

			self.customer_invoice = records






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

class DocumentEcube(models.Model):
	_name = 'sii.document_type'

	name = fields.Char()

class EcubeCustomer(models.Model):
	_name = 'customer.search'


	name = fields.Many2one('res.partner',string="Customers")
	rut = fields.Char(string="Rut")

	@api.onchange('name')
	def get_rut(self):
		if self.name:
			rec = self.env['res.partner'].search([('id','=',self.name.id)])
			self.rut = rec.rut


	@api.onchange('rut')
	def get_name(self):
		if self.rut:
			rec = self.env['res.partner'].search([('rut','=',self.rut)])
			self.name = rec.id



	@api.multi
	def get_customer(self):
		rec = self.env['res.partner'].search([('id','=',self.name.id)]).id
		view_id = self.env.ref('vinsoft_customer.vinsoft_customer_form_view').id
		return {
				'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner',
                'view_id' : view_id,
                'target': 'main',
                'res_id': rec,
				}









	



