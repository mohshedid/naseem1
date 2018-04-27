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
    _name = 'report.customer_profile.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_profile.customer_report')
        active_wizard = self.env['customer.prof'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['customer.prof'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['customer.prof'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()
        
        records = self.env['res.partner'].search([('id','=',record_wizard.customer.id)])
        product = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])

        lissst = []
        for x in product:
            for y in x.invoice_line_ids:
                if y.product_id.name not in lissst:
                    lissst.append(y.product_id.name)


        def old_product(attr):
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                for z in x.invoice_line_ids:
                    if check < value5 and attr == z.product_id.name:
                        value = value + z.price_subtotal

            return value


        def get_product(attr):
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                test = str(date[:7])
                for z in x.invoice_line_ids:
                    if check == test and attr == z.product_id.name:
                        value = value + z.price_subtotal

            return value


        def get_product1(attr):
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                for z in x.invoice_line_ids:
                    if check == value1 and attr == z.product_id.name:
                        value = value + z.price_subtotal

            return value


        def get_product2(attr):
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                for z in x.invoice_line_ids:
                    if check == value2 and attr == z.product_id.name:
                        value = value + z.price_subtotal

            return value


        def get_product3(attr):
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                for z in x.invoice_line_ids:
                    if check == value3 and attr == z.product_id.name:
                        value = value + z.price_subtotal

            return value


        def get_product4(attr):
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                for z in x.invoice_line_ids:
                    if check == value4 and attr == z.product_id.name:
                        value = value + z.price_subtotal

            return value


        def get_product5(attr):
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                for z in x.invoice_line_ids:
                    if check == value5 and attr == z.product_id.name:
                        value = value + z.price_subtotal

            return value


        def get_sale():
            value = 0 
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                test = str(date[:7])
                if check == test:
                    value = value + x.amount_total

            return value


        def get_val1():
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                if check == value1:
                    value = value + x.amount_total

            return value


        def get_val2():
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                if check == value2:
                    value = value + x.amount_total

            return value


        def get_val3():
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                if check == value3:
                    value = value + x.amount_total

            return value
            

        def get_val4():
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                if check == value4:
                    value = value + x.amount_total

            return value

        def get_val5():
            value = 0
            sale = self.env['account.invoice'].search([('partner_id.id','=',record_wizard.customer.id),('type','=','out_invoice')])
            for x in sale:
                check = str(x.date_invoice[:7])
                if check == value5:
                    value = value + x.amount_total

            return value


        customer = record_wizard.customer.name
        date = record_wizard.date


        reporting_months = []       
        year = int(date[:4])
        month = int(date[5:7])
        print month
        day = int(date[8:10])
        months_in_words = {
        1:'Jan',
        2:'Feb',
        3:'March',
        4:'April',
        5:'May',
        6:'June',
        7:'July',
        8:'August',
        9:'September',
        10:'Octuber',
        11:'November',
        12:'December',
        }
        current = month
        for x in range(0,5):
            if current == 1:
                current = 12
            else:
                current = current - 1 
            reporting_months.append(months_in_words[current])



        reporting_date = []
        new_y = int(date[:4])
        new_8 = int(date[:4])
        new_9 = int(date[:4])
        new_10 = int(date[:4])
        new_11 = int(date[:4])
        new_12 = int(date[:4])
        new_m = int(date[5:7])
        if new_m == 1:
            new_12 = new_12 - 1
            new_11 = new_11 - 1
            new_10 = new_10 - 1
            new_9 = new_9 - 1
            new_8 = new_8 - 1
        if new_m == 2:
            new_12 = new_12 - 1
            new_11 = new_11 - 1
            new_10 = new_10 - 1
            new_9 = new_9 - 1
        if new_m == 3:
            new_12 = new_12 - 1
            new_11 = new_11 - 1
            new_10 = new_10 - 1
        if new_m == 4:
            new_12 = new_12 - 1
            new_11 = new_11 - 1
        if new_m == 5:
            new_12 = new_12 - 1

        months_in_words = {
        1:str(new_y)+'-01',
        2:str(new_y)+'-02',
        3:str(new_y)+'-03',
        4:str(new_y)+'-04',
        5:str(new_y)+'-05',
        6:str(new_y)+'-06',
        7:str(new_y)+'-07',
        8:str(new_8)+'-08',
        9:str(new_9)+'-09',
        10:str(new_10)+'-10',
        11:str(new_11)+'-11',
        12:str(new_12)+'-12',
        }
        now = month
        for x in range(0,5):
            if now == 1:
                now = 12
            else:
                now = now - 1 
            reporting_date.append(months_in_words[now])


        for line in reporting_date[:1]:
            value1 = line
        for line in reporting_date[1:2]:
            value2 = line
        for line in reporting_date[2:3]:
            value3 = line
        for line in reporting_date[3:4]:
            value4 = line
        for line in reporting_date[4:5]:
            value5 = line


        docargs = {
        
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': records,
            'data': data,
            'customer': customer,
            'date': date,
            'get_sale': get_sale,
            'reporting_months': reporting_months,
            'get_val1': get_val1,
            'get_val2': get_val2,
            'get_val3': get_val3,
            'get_val4': get_val4,
            'get_val5': get_val5,
            'lissst': lissst,
            'get_product': get_product,
            'old_product': old_product,
            'get_product1': get_product1,
            'get_product2': get_product2,
            'get_product3': get_product3,
            'get_product4': get_product4,
            'get_product5': get_product5,

            }

        return report_obj.render('customer_profile.customer_report', docargs)