#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################
from openerp import models, fields, api


class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.customer_balances.module_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_balances.module_report')
        records = self.env['res.partner'].browse(docids)


        def get_date(attr):
            last = []
            name = " "
            cust = self.env['account.invoice'].search([(('type','=',"out_invoice"))])
            for x in cust:
                if x.partner_id.id == attr:
                    last.append(x)
                    newlist = sorted(last, key=lambda x: x.date_invoice)
                    name = newlist.pop().date_invoice

            return name

        def get_amt(attr):
            last = []
            name = " "
            cust = self.env['account.invoice'].search([(('type','=',"out_invoice"))])
            for x in cust:
                if x.partner_id.id == attr:
                    last.append(x)
                    newlist = sorted(last, key=lambda x: x.date_invoice)
                    name = newlist.pop().amount_total

            return name


        def get_part(attr):
            last = []
            name = " "
            cust = self.env['customer.payment.bcube'].search([(('receipts','=',True))])
            for x in cust:
                if x.partner_id.id == attr:
                    last.append(x)
                    newlist = sorted(last, key=lambda x: x.date)
                    name = newlist.pop().date

            return name


        def get_paid(attr):
            last = []
            name = " "
            cust = self.env['customer.payment.bcube'].search([(('receipts','=',True))])
            for x in cust:
                if x.partner_id.id == attr:
                    last.append(x)
                    newlist = sorted(last, key=lambda x: x.date)
                    name = newlist.pop().amount

            return name



        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': records,
            'data': data,
            'get_date': get_date,
            'get_amt': get_amt,
            'get_part': get_part,
            'get_paid': get_paid,


            }

        return report_obj.render('customer_balances.module_report', docargs)