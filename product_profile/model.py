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
import re
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.product_profile.profile_product'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_profile.profile_product')
        active_wizard = self.env['product.profile.wizard'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.profile.wizard'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['product.profile.wizard'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        product = record_wizard.product.name
        product_id = record_wizard.product.id

        amount = record_wizard.product.list_price_own
        level1 = record_wizard.product.level_1
        level2 = record_wizard.product.level_2
        level3 = record_wizard.product.level_3
        date = record_wizard.date

        reporting_months_names = []
        reporting_months = []

        def date_getter():
            del reporting_months_names[:]        
            del reporting_months[:]         
            year = int(date[:4])
            month = int(date[5:7])
            day = int(date[8:10])
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
            current = month
            crr_yr = year
            for x in range(0,6):
                if current == 1:
                    current = 12
                    crr_yr = crr_yr - 1
                else:
                    current = current - 1

                reporting_months_names.append(months_in_words[current])
                reporting_months.append((str(current) + ',' + str(crr_yr)))
            print reporting_months
            print "-----------------------------------"

            month = months_in_words[month]
            return "%s %s %s" %(day,month,year)

        def time_getter():
            time = str(date[11:16])
            return time

        records = self.env['account.invoice'].search([('type','=','out_invoice')])

        date_wise = []
        prod_wise = []
        customers = []
        def recording():
            del date_wise[:]
            del prod_wise[:]
            del customers[:]
            dated = ' '
            for x in records:
                if x.date_invoice:
                    dated = str(int(x.date_invoice[5:7])) + ',' + str(int(x.date_invoice[:4]))
                    if dated in reporting_months:
                        date_wise.append(x)

            for x in date_wise:
                for y in x.invoice_line_ids:
                    if y.product_id.name == product:
                        prod_wise.append(x)

            for x in prod_wise:
                if customers == []:
                    customers.append(x.partner_id)
                else:
                    if x.partner_id not in customers:
                        customers.append(x.partner_id)

        def getdata(cust,attr):
            active_invoices = []
            for x in prod_wise:
                if x.partner_id.id == cust.id:
                    active_invoices.append(x)
            customer = self.env['res.partner'].search([('id','=',cust.id)])
            if attr == 'mobile':
                return customer.mobile
            if attr == 'mobile2':
                return customer.mobile2

        def getamount(cust,month):
            active_invoices = []
            for x in prod_wise:
                if x.partner_id.id == cust.id:
                    active_invoices.append(x)
            customer = self.env['res.partner'].search([('id','=',cust.id)])
            months_in_names = {
            'Jan':1,
            'Feb':2,
            'March':3,
            'April':4,
            'May':5,
            'June':6,
            'July':7,
            'Aug':8,
            'Sep':9,
            'Oct':10,
            'Nov':11,
            'Dec':12,
            }
            report_month =  months_in_names[month]
            amount = 0
            for x in active_invoices:
                active_invoice_date = int(x.date_invoice[5:7])
                if active_invoice_date == report_month:
                    for y in x.invoice_line_ids:
                        if y.product_id.id == product_id:
                            amount = amount + y.quantity

            return amount

        def olddata(cust):
            old_invoices = []
            old_quant = 0
            last_month = reporting_months[5]
            splited = last_month.split(',')
            month = int(splited[0])
            year = int(splited[1])
            for x in records:
                inv_month = int(x.date_invoice[5:7])
                inv_yr = int(x.date_invoice[:4])
                if inv_yr < year:
                    old_invoices.append(x)
                if inv_yr == year:
                    if inv_month < month:
                        old_invoices.append(x)

            for x in old_invoices:
                for y in x.invoice_line_ids:
                    if y.product_id.id == product_id:
                        old_quant = old_quant + y.quantity

            return old_quant


        docargs = {
            'doc_ids': docids,
            'doc_model': 'product.product',
            'docs': records,
            'data': data,
            'date_getter': date_getter,
            'time_getter': time_getter,
            'product': product,
            'amount': amount,
            'level1': level1,
            'level2': level2,
            'level3': level3,
            'reporting_months_names': reporting_months_names,
            'recording': recording,
            'customers': customers,
            'getdata': getdata,
            'getamount': getamount,
            'olddata': olddata
        }

        return report_obj.render('product_profile.profile_product', docargs)