#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.customer_recipt.customer_recipts'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_recipt.customer_recipts')
        active_wizard = self.env['customer.recipt.wizard'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['customer.recipt.wizard'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['customer.recipt.wizard'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        users = record_wizard.users

        date = datetime.now().date()
        timed = datetime.now().time().strftime("%H:%M")

        records = self.env['customer.payment.bcube'].search([])

        users_list = []
        for x in users:
            users_list.append(x)

        # def customer(attr):
        #     count = 0
        #     first = ' '
        #     last = ' '
        #     for x in users_list:
        #         last = x.name
        #         count = count + 1

        #     if count == 1:
        #         first = users.name
        #     else:
        #         first_user = users_list[0]
        #         first = first_user.name

        #     if attr == 'first':
        #         return first

        #     if attr == 'last':
        #         return last

        def getloop(attr):
            loops = 0
            recipts = self.env['customer.payment.bcube'].search([('active_user','=',attr.id),('date','>=',form),('date','<=',to),('receipts','=',True)])
            for x in recipts:
                loops = loops + 1

            return loops

        user_recipts = []
        def getrecipts(attr):
            del user_recipts[:]
            recipts = self.env['customer.payment.bcube'].search([('active_user','=',attr.id),('date','>=',form),('date','<=',to),('receipts','=',True)])
            for x in recipts:
                user_recipts.append(x)


        def get_time():
            t0 = time.time()
            t1 = t0 + (60*60)*5 
            new = time.strftime("%I:%M",time.localtime(t1))

            return new

        docargs = {
            'doc_ids': docids,
            'doc_model': 'customer.payment.bcube',
            'docs': records,
            'data': data,
            'to': to,
            'form': form,
            # 'customer': customer,
            'date': date,
            'timed': timed,
            'users_list': users_list,
            'getrecipts': getrecipts,
            'user_recipts': user_recipts,
            'getloop': getloop,
            'get_time': get_time,
        }

        return report_obj.render('customer_recipt.customer_recipts', docargs)