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
    _name = 'report.product_price_list.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_price_list.customer_report')
        active_wizard = self.env['product.list'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.list'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['product.list'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        product = record_wizard.product
        slect_prod = record_wizard.slect_prod

        
        records = self.env['product.product'].search([])

        select = []
        records = self.env['product.product'].search([])
        for x in slect_prod:
            for z in records:
                if x.id == z.id:
                    select.append(z)

        count = [1]



        def namer():
            prov = ""
            if product == "all_prod":
                prov = product
            if product == "multi_prod":
                prov = product

            return prov



        docargs = {

            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': count,
            'data': data,
            'records': records,
            'namer': namer,
            'select': select,

            }

        return report_obj.render('product_price_list.customer_report', docargs)