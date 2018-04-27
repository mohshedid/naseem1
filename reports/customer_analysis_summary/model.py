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
    _name = 'report.customer_analysis_summary.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_analysis_summary.customer_report')
        active_wizard = self.env['customer.analysis'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['customer.analysis'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['customer.analysis'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        form = record_wizard.form
        to = record_wizard.to
        
        records = self.env['res.partner'].search([])

        def get_open(attr):
            value = 0
            deb = 0
            cre = 0
            balance = self.env['account.move'].search([('date','<=',form)])
            for x in balance:
                for z in x.line_ids:
                    if z.partner_id.id == attr:
                        if z.account_id.user_type_id.name == "Receivable":
                            deb = deb + z.debit
                            cre = cre + z.credit
                            value = deb - cre

            return value

        def get_sale(attr):
            value = 0 
            sale = self.env['account.invoice'].search([('type','=','out_invoice'),('date_invoice','>=',form),('date_invoice','<=',to)])
            for x in sale:
                if attr == x.partner_id.id:
                    value = value + x.amount_total

            return value


        def get_receipt(attr):
            value = 0 
            cust = self.env['customer.payment.bcube'].search([('receipts','=',True),('date','>=',form),('date','<=',to)])
            for x in cust:
                if attr == x.partner_id.id:
                    value = value + x.amount

            return value



        count = [1]

        def get_form():
            name = ""
            name = form

            return name

        def get_to():
            name = ""
            name = to

            return name


        docargs = {

            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': count,
            'data': data,
            'get_form': get_form,
            'get_to': get_to,
            'records': records,
            'get_open': get_open,
            'get_sale': get_sale,
            'get_receipt': get_receipt,

            }

        return report_obj.render('customer_analysis_summary.customer_report', docargs)