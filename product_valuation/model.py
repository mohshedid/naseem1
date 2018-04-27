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
import time

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.product_valuation.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_valuation.customer_report')
        active_wizard = self.env['product.valuation'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.valuation'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['product.valuation'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        product = record_wizard.product
        slect_prod = record_wizard.slect_prod
        slect_categ = record_wizard.slect_categ

        
        records = self.env['product.product'].search([])

        select = []
        records = self.env['product.product'].search([])
        for x in slect_prod:
            for z in records:
                if x.id == z.id:
                    select.append(z)

        cat = []
        records = self.env['product.product'].search([])
        for z in records:
            if z.categ_id.id == slect_categ.id:
                cat.append(z)


        count = [1]

        def hand(attr):
            amt = 0
            last = []
            name = " "
            stock = 0
            data = self.env['stock.history'].search([('product_id.id','=',attr)])
            for x in data:
                amt = amt + x.quantity
                last.append(x)
                newlist = sorted(last, key=lambda x: x.date)
                name = newlist.pop().date
            for x in data:
                if name == x.date:
                    stock = stock + x.quantity

            return amt,stock

        def get_time():
            t0 = time.time()
            t1 = t0 + (60*60)*5 
            new = time.strftime("%I:%M",time.localtime(t1))

            return new


        def namer():
            prov = ""
            if product == "all_prod":
                prov = product
            if product == "multi_prod":
                prov = product
            if product == "categ_wise":
                prov = product

            return prov



        docargs = {

            'doc_ids': docids,
            'doc_model': 'product.product',
            'docs': count,
            'data': data,
            'records': records,
            'namer': namer,
            'select': select,
            'cat': cat,
            'hand': hand,
            'get_time': get_time,

            }

        return report_obj.render('product_valuation.customer_report', docargs)