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
    _name = 'report.customer_top_sale.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_top_sale.customer_report')
        active_wizard = self.env['customer.top.sale'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['customer.top.sale'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['customer.top.sale'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        customer = record_wizard.customer
        form = record_wizard.form
        to = record_wizard.to
        sale_abv = record_wizard.sale_abv
        slect_cust = record_wizard.slect_cust
        slect_custmr = record_wizard.slect_custmr

        
        records = self.env['account.invoice'].search([('type','=',"out_invoice"),('date_invoice','>=',form),('date_invoice','<=',to)])
        count = [1]



        multi = []
        if customer == "multi_cust":
            for x in slect_cust:
                multi.append(x.name)


        top = []
        if customer == "top_cust":
            for x in records:
                if x.partner_id.name not in top:
                    top.append(x.partner_id.name)


        def get_top(attr):
            value = 0 
            for x in records:
                if attr == x.partner_id.name:
                    value = value + x.amount_total

            return value

        
        select = []
        if customer == "top_cust":
            for x in top:
                amt = 0
                for z in records:
                    if x == z.partner_id.name:
                        amt = amt + z.amount_total
                if amt > sale_abv:
                    select.append(x)


        def get_multi(attr):
            value = 0 
            for x in records:
                if attr == x.partner_id.name:
                    value = value + x.amount_total

            return value


        def get_all():
            value = 0 
            for x in records:
                value = value + x.amount_total

            return value


        def get_spec():
            value = 0 
            for x in records:
                if x.partner_id.id == record_wizard.slect_custmr.id:
                    value = value + x.amount_total

            return value


        def get_name():
            name = ""
            if customer == "spec_cust":
                name = slect_custmr.name

            return name

        def get_form():
            name = ""
            name = form

            return name

        def get_to():
            name = ""
            name = to

            return name

        def get_id(attr):
            name = 0
            if customer == "spec_cust" and attr == 'id':
                name = slect_custmr.id
            if customer == "multi_cust":
                for x in slect_cust:
                    if attr == x.name:
                        name = x.id
            if customer == "top_cust":
                for x in records:
                    if attr == x.partner_id.name:
                        name = x.partner_id.id

            return name


        def namer():
            prov = ""
            if customer == "top_cust":
                prov = customer
            if customer == "all_cust":
                prov = customer
            if customer == "spec_cust":
                prov = customer
            if customer == "multi_cust":
                prov = customer

            return prov



        docargs = {

            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': count,
            'data': data,
            'get_all': get_all,
            'get_spec': get_spec,
            'namer': namer,
            'get_name': get_name,
            'get_id': get_id,
            'get_multi': get_multi,
            'multi': multi,
            'top': top,
            'get_form': get_form,
            'get_to': get_to,
            'select': select,
            'get_top': get_top

            }

        return report_obj.render('customer_top_sale.customer_report', docargs)