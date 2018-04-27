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
    _name = 'report.product_valuation_summary.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_valuation_summary.customer_report')
        active_wizard = self.env['product.valuation.summary'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.valuation.summary'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['product.valuation.summary'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        slect_prod = record_wizard.slect_prod

        select = []
        records = self.env['product.category'].search([])
        for x in slect_prod:
            for z in records:
                if x.id == z.id:
                    select.append(z)

        count = [1]

        def hand(attr):
            amt = 0
            data = self.env['stock.history'].search([])
            for x in data:
                if attr == x.product_categ_id.id:
                    amt = amt + x.quantity

            return amt


        def cost(attr):
            amt = 0
            new = 0
            data = self.env['stock.history'].search([])
            for x in data:
                if attr == x.product_categ_id.id:
                    new = x.quantity * x.product_id.average_cost
                    amt = amt + new

            return amt

        def first():
            name = " "
            for x in slect_prod:
                name = x.name

            return name


        def last():
            name = " "
            for x in slect_prod[:1]:
                name = x.name

            return name






        docargs = {

            'doc_ids': docids,
            'doc_model': 'product.category',
            'docs': count,
            'data': data,
            'select': select,
            'hand': hand,
            'cost': cost,
            'first': first,
            'last': last,
     

            }

        return report_obj.render('product_valuation_summary.customer_report', docargs)