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
    _name = 'report.partner_ledger_detail.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('partner_ledger_detail.customer_report')
        active_wizard = self.env['partner.ledger'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['partner.ledger'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['partner.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        form = record_wizard.form
        to = record_wizard.to
        partner_ids = record_wizard.partner_ids.name

        records = self.env['res.partner'].search([('id','=',record_wizard.partner_ids.id)])
        def get_bal(attr):
            value = 0
            deb = 0
            cre = 0
            balance = self.env['account.move'].search([('date','<=',form)])
            for x in balance:
                for z in x.line_ids:
                    if z.partner_id.id == attr:
                        if z.account_id.user_type_id.name == "Receivable":
                            deb = deb + z.debit
                            cre = cre + z.credit
                            value = deb - cre

            return value

        upper = []
        main = self.env['account.invoice'].search([('type','=','out_invoice'),('partner_id.id','=',record_wizard.partner_ids.id),('date_invoice','>=',form),('date_invoice','<=',to)])
        for x in main:
            upper.append(x)

        inner = []
        def get_line(attr):
            del inner[:]
            main = self.env['account.invoice'].search([('type','=','out_invoice'),('partner_id.id','=',record_wizard.partner_ids.id),('date_invoice','>=',form),('date_invoice','<=',to)])
            for x in main:
                if attr == x.id:
                    for z in x.invoice_line_ids:
                        inner.append(z)




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
            'doc_model': 'res.partner',
            'docs': records,
            'data': data,
            'get_form': get_form,
            'get_to': get_to,
            'get_bal': get_bal,
            'upper': upper,
            'get_line': get_line,
            'inner': inner,
            }

        return report_obj.render('partner_ledger_detail.customer_report', docargs)