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
    _name = 'report.sale_invoice_summary.module_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sale_invoice_summary.module_report')
        active_wizard = self.env['sale.invoice.summary'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['sale.invoice.summary'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['sale.invoice.summary'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        customer = record_wizard.customer
        slect_cust = record_wizard.slect_cust
        form = record_wizard.form
        to = record_wizard.to
        invoice_from = record_wizard.invoice_from
        invoice_to = record_wizard.invoice_to
        
        records = self.env['account.invoice'].search([('type','=',"out_invoice"),('date_invoice','>=',form),('date_invoice','<=',to)])
        count = [1]

        multi = []
        if customer == "spec_cust":
            for x in slect_cust:
                for z in records:
                    if x.name == z.partner_id.name:
                        multi.append(z)


        def get_form():
            name = ""
            name = form

            return name

        def get_to():
            name = ""
            name = to

            return name

        def get_inv_from():
            name = ""
            name = invoice_from

            return name

        def get_inv_to():
            name = ""
            name = invoice_to

            return name

        def namer():
            prov = ""
            if customer == "all_cust":
                prov = customer
            if customer == "spec_cust":
                prov = customer

            return prov


      

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': count,
            'data': data,
            'get_form': get_form,
            'get_to': get_to,
            'get_inv_from': get_inv_from,
            'get_inv_to': get_inv_to,
            'multi': multi,
            'records': records,
            'namer': namer,
       
            }

        return report_obj.render('sale_invoice_summary.module_report', docargs)