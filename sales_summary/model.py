#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

import time
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SampleDevelopmentReport(models.AbstractModel):
	_name = 'report.sales_summary.sales_summary_report'

	@api.model
	def render_html(self,docids, data=None):

		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sales_summary.sales_summary_report')
		active_wizard = self.env['sales.summary'].search([])

		emp_list = []
		for x in active_wizard:
			emp_list.append(x.id)
		emp_list = emp_list
		emp_list_max = max(emp_list) 

		record_wizard = self.env['sales.summary'].search([('id','=',emp_list_max)])
		record_wizard_del = self.env['sales.summary'].search([('id','!=',emp_list_max)])
		record_wizard_del.unlink()

		to = record_wizard.to
		form = record_wizard.form

		date = datetime.now().date()
		
		records = self.env['account.invoice'].search([('type','in',('out_invoice','out_refund')),('state','not in',('draft','cancel')),('journal_id.type','=','cash')])

		start_date = datetime.strptime(form,"%Y-%m-%d")
		end_date = datetime.strptime(to,"%Y-%m-%d")
		lisst = []
		 
		if start_date <= end_date:
			for n in range( ( end_date - start_date ).days + 1 ):
				lisst.append( start_date + timedelta( n ) )
		else:
			for n in range( ( start_date - end_date ).days + 1 ):
				lisst.append( start_date - timedelta( n ) )
		 
		# for d in list:
		# 	testdate = str(d).split(' ')
		# 	print testdate[0]

		# def cashsale(attr):
		# 	direct_invoices = self.env['sale.order'].search([('direct_invoice_check','=','1'),('date_order','=',attr)])
		# 	direct_payments = 0
		# 	for x in direct_invoices:
		# 		if testdate == attr:
		# 			print "kkkkkkkkkkkkkkkkkkkkkkkkk"
		# 			direct_payments = direct_payments + x.amount_total

		# 	return direct_payments

		def creditsale(attr):
			credit_invoices = self.env['account.invoice'].search([('date_invoice','=',attr),('type','in',('out_invoice','out_refund')),('journal_id.type','!=','cash'),('state','not in',('draft','cancel'))])
			credit_payments = 0
			for x in credit_invoices:
				credit_payments = credit_payments + x.amount_total

			return credit_payments

		def cashsale(attr):
			cash_invoices = self.env['account.invoice'].search([('date_invoice','=',attr),('type','in',('out_invoice','out_refund')),('journal_id.type','=','cash'),('state','not in',('draft','cancel'))])
			cash_payments = 0
			for x in cash_invoices:
				cash_payments = cash_payments + x.amount_total

			return cash_payments

		def cashpay(attr):
			cash_payments = self.env['customer.payment.bcube'].search([('date','=',attr),('journal_id.type','=','cash'),('receipts','=',True)])
			cash_payment = 0
			for x in cash_payments:
				cash_payment = cash_payment + x.total

			return cash_payment

		def bankpay(attr):
			bank_payments = self.env['customer.payment.bcube'].search([('date','=',attr),('journal_id.type','=','bank'),('receipts','=',True)])
			bank_payment = 0
			for x in bank_payments:
				bank_payment = bank_payment + x.total

			return bank_payment

		def get_time():
			t0 = time.time()
			t1 = t0 + (60*60)*5 
			new = time.strftime("%I:%M",time.localtime(t1))

			return new


		docargs = {
			'doc_ids': docids,
			'doc_model': 'account.invoice',
			'docs': records,
			'data': data,
			'to':to,
			'form':form,
			'date':date,
			'cashsale': cashsale,
			'creditsale': creditsale,
			'cashpay': cashpay,
			'bankpay': bankpay,
			'lisst': lisst,
			'get_time': get_time,
		}

		return report_obj.render('sales_summary.sales_summary_report', docargs)