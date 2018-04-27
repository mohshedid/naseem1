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

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.product_profit.product_profit'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_profit.product_profit')
        active_wizard = self.env['product.profit.wizard'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.profit.wizard'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['product.profit.wizard'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        products = record_wizard.products
        prod_catag = record_wizard.category
        date = datetime.now()

        
        p_qunat = 0
        for x in products:
            p_qunat = p_qunat + 1
            last_prod = x.name

        if p_qunat == 1:
            first_prod = last_prod
        else:
            first_prod = products[1].name
        
        c_qunat = 0
        for x in prod_catag:
            c_qunat = c_qunat + 1
            last_cat = x.name
        
        if c_qunat == 1:
            first_cat = last_cat
        else:
            first_cat = prod_catag[1].name
            

        records = self.env['account.invoice'].search([('date_invoice','>=',form),('date_invoice','<=',to)])

        def date_getter():
            year = int(date.year)
            month = int(date.month)
            day = int(date.day)
            months_in_words = {
             1:'Jan',
             2:'Feb',
             3:'March',
             4:'April',
             5:'May',
             6:'June',
             7:'July',
             8:'Aug',
             9:'Sep',
            10:'Oct',
            11:'Nov',
            12:'Dec',
            }

            month = months_in_words[month]
            return "%s %s %s" %(day,month,year)

        def time_getter():
            return date.time()

        active_invoices = []
        def get_records(prod):
            del active_invoices[:]
            for x in records:
                for y in x.invoice_line_ids:
                    if y.product_id == prod:
                        active_invoices.append(x)

        def lines_data(data,attr,prod):
            invoiced = self.env['account.invoice'].search([('id','=',data.id)])
            if attr == 'sale_price':
                for x in invoiced.invoice_line_ids:
                    if x.product_id == prod:
                        return x.price_unit

            if attr == 'quant':
                for x in invoiced.invoice_line_ids:
                    if x.product_id == prod:
                        return x.quantity

            if attr == 'quant':
                for x in invoiced.invoice_line_ids:
                    if x.product_id == prod:
                        return x.quantity
            
        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'data': data,
            'date_getter': date_getter,
            'time_getter': time_getter,
            'to': to,
            'form': form,
            'first_prod': first_prod,
            'last_prod': last_prod,
            'first_cat': first_cat,
            'last_cat': last_cat,
            'products': products,
            'get_records': get_records,
            'active_invoices': active_invoices,
            'lines_data': lines_data
        }

        return report_obj.render('product_profit.product_profit', docargs)