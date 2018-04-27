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
    _name = 'report.stock_checking_report.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_checking_report.customer_report')
        active_wizard = self.env['stock.check'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['stock.check'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['stock.check'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        slect_loc = record_wizard.slect_loc
        location = record_wizard.location
        date = record_wizard.date

        count=[1]

        lisst = []
        records = self.env['stock.history'].search([('location_id.name','=',record_wizard.slect_loc.name)])
        for x in records:
            if x.product_id.id not in lisst:
                lisst.append(x.product_id.id)

        new = []
        records = self.env['stock.history'].search([])
        for x in records:
            if x.product_id.id not in new:
                new.append(x.product_id.id)


        def get_name(attr):
            name = " "
            if record_wizard.location == "all_loc":
                records = self.env['stock.history'].search([])
            else:
                records = self.env['stock.history'].search([('location_id.name','=',record_wizard.slect_loc.name)])
            for x in records:
                if x.product_id.id == attr:
                    name = x.product_id.name


            return name

        def get_cat(attr):
            name = " "
            if record_wizard.location == "all_loc":
                records = self.env['stock.history'].search([])
            else:
                records = self.env['stock.history'].search([('location_id.name','=',record_wizard.slect_loc.name)])
            for x in records:
                if x.product_id.id == attr:
                    name = x.product_id.categ_id.name

            return name


        # def get_caton(attr):
        #     value = 0
        #     if record_wizard.location == "all_loc":
        #         records = self.env['stock.history'].search([])
        #     else:
        #         records = self.env['stock.history'].search([('location_id.name','=',record_wizard.slect_loc.name)])
        #     for x in records:
        #         if x.product_id.id == attr:
        #             value = value + x.product_id.pcs_per_carton

        #     return value


        def get_quan(attr):
            value = 0
            if record_wizard.location == "all_loc":
                records = self.env['stock.history'].search([])
            else:
                records = self.env['stock.history'].search([('location_id.name','=',record_wizard.slect_loc.name)])
            for x in records:
                if x.product_id.id == attr:
                    value = value + x.quantity

            return value


        def get_caton(attr):
            value = 0
            carton = 0
            if record_wizard.location == "all_loc":
                records = self.env['stock.history'].search([])
            else:
                records = self.env['stock.history'].search([('location_id.name','=',record_wizard.slect_loc.name)])
            for x in records:
                if x.product_id.id == attr:
                    value = value + x.quantity
                    carton = value / x.product_id.pcs_per_carton

            return carton

        def get_loc():
            name = " "
            name = slect_loc = record_wizard.slect_loc.name
            return name


        def namer():
            prov = ""
            if location == "all_loc":
                prov = location
            if location == "multi_loc":
                prov = location

            return prov




        docargs = {

            'doc_ids': docids,
            'doc_model': 'product.category',
            'docs': count,
            'data': data,
            'lisst': lisst,
            'new': new,
            'get_name': get_name,
            'get_cat': get_cat,
            'get_caton': get_caton,
            'get_quan': get_quan,
            'get_loc': get_loc,
            'namer': namer,
     
            }

        return report_obj.render('stock_checking_report.customer_report', docargs)