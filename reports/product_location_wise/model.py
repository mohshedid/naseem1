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
    _name = 'report.product_location_wise.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_location_wise.customer_report')
        active_wizard = self.env['product.location'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.location'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['product.location'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        slect_prod = record_wizard.slect_prod
        product = record_wizard.product


        count=[1]
        check = [8]

        records = self.env['product.product'].search([])

        loc = []
        if product == "all_prod":
            record = self.env['stock.history'].search([])
            for x in record:
                if x.location_id.name not in loc:
                    loc.append(x.location_id.name)

        new_loc = []
        if product == "multi_prod":
            record = self.env['stock.history'].search([])
            for x in record:
                for z in slect_prod:
                    if z.id == x.product_id.id and x.location_id.name not in new_loc:
                        new_loc.append(x.location_id.name)


        multi = []
        if product == "multi_prod":
            for x in slect_prod:
                multi.append(x)


        def get_amt(attr,num):
            amt = 0
            data = self.env['stock.history'].search([])
            for x in data:
                if attr == x.product_id.id and num == x.location_id.name:
                    amt = amt + x.quantity

            return amt 





        def namer():
            prov = ""
            if product == "all_prod":
                prov = product
            if product == "multi_prod":
                prov = product

            return prov




        docargs = {

            'doc_ids': docids,
            'doc_model': 'product.category',
            'docs': count,
            'data': data,
            'namer': namer,
            'loc': loc,
            'new_loc': new_loc,
            'multi': multi,
            'get_amt': get_amt,
            'records': records,
     
            }

        return report_obj.render('product_location_wise.customer_report', docargs)