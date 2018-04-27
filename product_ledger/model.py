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
    _name = 'report.product_ledger.product_ledger_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_ledger.product_ledger_report')
        active_wizard = self.env['product.ledger'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.ledger'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['product.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        product = record_wizard.product

        date = datetime.now().date()
        timed = datetime.now().time().strftime("%H:%M")

        records = self.env['product.product'].search([('id','=',product.id)])

        invoices = self.env['stock.history'].search([('date','>=',form),('date','<=',to)])
        open_bal = self.env['stock.history'].search([('date','<',form)])


        required_invoices = []
        for x in invoices:
            if x.product_id == product:
                required_invoices.append(x)

        def get_tot():
            amt = 0
            for x in invoices:
                if x.product_id == product:
                    amt = amt + x.quantity

            return amt

        def get_open():
            amt = 0
            for x in open_bal:
                if x.product_id == product:
                    amt = amt + x.quantity

            return amt

        def get_time():
            t0 = time.time()
            t1 = t0 + (60*60)*5 
            new = time.strftime("%I:%M",time.localtime(t1))

            return new

        def get_price():
            amt = 0
            last = []
            last_d = []
            name = 0
            new = " "
            l_date = " "
            pcs = " "
            value = 0
            for x in invoices:
                if x.product_id == product:
                    pcs = x.product_id.uom
                    value = value + x.quantity
                    if x.quantity > 0:
                        last.append(x)
                        newlist = sorted(last, key=lambda x: x.id)
                        name = newlist.pop().id
                        last.append(x)
                        datelist = sorted(last, key=lambda x: x.date)
                        new = datelist.pop().date
            for x in invoices:
                if x.product_id == product:
                    if x.quantity > 0:
                        if x.id == name:
                            amt = x.quantity
                        if x.date == new:
                            l_date = x.date

            return amt,l_date,pcs,value






        # last_purchase = self.env['account.invoice'].search([('type','=','in_invoice'),('date_invoice','<',form)])

        # last_purchased = []
        # dates = []
        # for x in last_purchase:
        #     for y in x.invoice_line_ids:
        #         if y.product_id == product:
        #             last_purchased.append(x)
        #             dates.append(x.date_invoice)

        # dates.sort()

        # for x in dates:
        #     last = x

        # def last_quantity(attr):
        #     for x in last_purchased:
        #         if x.date_invoice == last:
        #             for y in x.invoice_line_ids:
        #                 if y.product_id == product:
        #                     if attr == 'qty':
        #                         return y.quantity
        #                     if attr == 'date':
        #                         return x.date_invoice
        #                     if attr == 'unit':
        #                         return y.product_id.uom

        

        # def line_data(data,attr):
        #     for x in required_invoices:
        #         if x == data:
        #             for y in x.invoice_line_ids:
        #                 if y.product_id == product:
        #                     if attr == 'unit_price':
        #                         return y.price_unit
        #                     if attr == 'qty':
        #                         return y.quantity
            
        docargs = {
            'doc_ids': docids,
            'doc_model': 'product.product',
            'docs': records,
            'data': data,
            'to': to,
            'form': form,
            'date': date,
            'timed': timed,
            'get_tot': get_tot,
            'get_price': get_price,
            'get_open': get_open,
            'get_time': get_time,
            'required_invoices': required_invoices,
            # 'line_data': line_data,
            # 'last_quantity': last_quantity
        }

        return report_obj.render('product_ledger.product_ledger_report', docargs)