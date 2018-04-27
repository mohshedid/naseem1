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
    _name = 'report.general_ledger_activity.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('general_ledger_activity.customer_report')
        active_wizard = self.env['general.ledger'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['general.ledger'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['general.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        form = record_wizard.form
        to = record_wizard.to
        account = record_wizard.account

        # records = self.env['account.move'].search([('id','=',record_wizard.partner_ids.id)])

        count = [1]

        lisst = []
        for x in account:
            lisst.append(x)


        inner = []
        def get_line(attr):
            del inner[:]
            main = self.env['account.move'].search([('date','>=',form),('date','<=',to)])
            for x in main:
                for z in x.line_ids:
                    if attr == z.account_id.code:
                        inner.append(z)

        def get_bal(attr):
            value = 0
            deb = 0
            cre = 0
            balance = self.env['account.move'].search([('date','<=',form)])
            for x in balance:
                for z in x.line_ids:
                    if z.account_id.code == attr:
                        deb = deb + z.debit
                        cre = cre + z.credit
                        if z.account_id.acct_type == "debit":
                            value = deb - cre
                        if z.account_id.acct_type == "credit":
                            value = cre - deb

            return value


        def get_form():
            name = ""
            name = form

            return name

        def get_to():
            name = ""
            name = to

            return name


        docargs = {

            'doc_ids': docids,
            'doc_model': 'account.account',
            'docs': count,
            'data': data,
            'get_form': get_form,
            'get_to': get_to,
            'lisst': lisst,
            'get_line': get_line,
            'inner': inner,
            'get_bal': get_bal,
            }

        return report_obj.render('general_ledger_activity.customer_report', docargs)