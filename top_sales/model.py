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
import time

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.top_sales.top_sales_wise'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('top_sales.top_sales_wise')
        active_wizard = self.env['topsales.wizard'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['topsales.wizard'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['topsales.wizard'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        report_type = record_wizard.report_type
        prod_catag = record_wizard.category

        date = datetime.now().date()
        timed = datetime.now().time().strftime("%H:%M")

        records = self.env['account.invoice'].search([('date_invoice','>',form),('date_invoice','<',to),('type','in',('out_invoice','out_refund')),('state','not in',('draft','cancel'))])
        entries = []
        for x in records:
            if x.partner_id.city not in entries:
                entries.append(x.partner_id.city)

        def getamount(city):
            total_of_city = 0
            if prod_catag:
                for x in records:
                    if x.partner_id.city == city:
                        for y in x.invoice_line_ids:
                            if y.product_id.categ_id.id == prod_catag.id:
                                total_of_city = total_of_city + y.price_subtotal
            else:
                for x in records:
                    if x.partner_id.city == city:
                        total_of_city = total_of_city + x.amount_total

            return total_of_city


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
            'to': to,
            'form': form,
            'date': date,
            'timed': timed,
            'entries': entries,
            'getamount': getamount,
            'get_time': get_time,
        }

        return report_obj.render('top_sales.top_sales_wise', docargs)