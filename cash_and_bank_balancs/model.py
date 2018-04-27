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
    _name = 'report.cash_and_bank_balancs.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cash_and_bank_balancs.customer_report')
        active_wizard = self.env['cash.bank'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['cash.bank'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['cash.bank'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        to = record_wizard.to

        # records = self.env['account.move'].search([('id','=',record_wizard.partner_ids.id)])

        count = [1]

        bank = []
        def get_bank():
            records = self.env['account.move'].search([('date','<=',record_wizard.to)])
            print records
            print "kkkkkkkkkkkkkkkkkkkkkk"
            for x in records:
                for z in x.line_ids:
                    if z.account_id.user_type_id.name == "Bank and Cash":
                        if z.account_id.name not in bank:
                            bank.append(z.account_id.name)


        print get_bank()
        print "============================"


        def get_cr(attr):
            value = 0
            records = records = self.env['account.move'].search([('date','<=',record_wizard.to)])
            for x in records:
                for z in x.line_ids:
                    if attr == z.account_id.name:
                        value = value + z.credit

            return value


        def get_dr(attr):
            value = 0
            records = records = self.env['account.move'].search([('date','<=',record_wizard.to)])
            for x in records:
                for z in x.line_ids:
                    if attr == z.account_id.name:
                        value = value + z.debit

            return value


        def get_date():
            value = " "
            value = record_wizard.to

            return value



        docargs = {

            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': count,
            'data': data,
            'bank': bank,
            'get_cr': get_cr,
            'get_dr': get_dr,
            'get_date': get_date,
            }

        return report_obj.render('cash_and_bank_balancs.customer_report', docargs)