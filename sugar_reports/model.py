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
##############################################################################
from openerp import models, fields, api
from datetime import date

class EmployeeGatepass(models.AbstractModel):
    _name = 'report.sugar_reports.funds_recovery'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sugar_reports.funds_recovery')
        active_wizard = self.env['funds.recovery'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['funds.recovery'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['funds.recovery'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        party = record_wizard.parties
        form = record_wizard.form
        to = record_wizard.to
        type_report = record_wizard.type_report
        parties_type = record_wizard.parties_type

        def getreportname():
            if type_report == "enty_level":
                return "Entry Level"

            if type_report == "clearance":
                return "Clearance"

            if type_report == "confirmation":
                return "Confirmation"

            if type_report == "enter_clear":
                return "Entry Level/Clearance"

        if parties_type == 'all':
            if type_report == 'enty_level':
                entry_level = self.env['funds.flow.tree'].search([('stages','=','entry')])
            if type_report == 'clearance':
                entry_level = self.env['funds.flow.tree'].search([('stages','=','clearing')])
            if type_report == 'enter_clear':
                entry_level = self.env['funds.flow.tree'].search(['|',('stages','=','clearing'),('stages','=','entry')])
            if type_report == 'confirmation':
                entry_level = self.env['funds.flow.tree'].search([('stages','=','confirmation'),('date','>=',form),('date','<=',to)])
            
            entries = []
            for x in entry_level:
                if x.party:
                    if x.party not in entries:
                        entries.append(x.party)
                if x.customer:
                    if x.customer not in entries:
                        entries.append(x.customer)
                if x.supplier:
                    if x.supplier not in entries:
                        entries.append(x.supplier)
        
        elif parties_type == 'specific':
            if type_report == 'enty_level':
                entry_level = self.env['funds.flow.tree'].search([('stages','=','entry')])
            if type_report == 'clearance':
                entry_level = self.env['funds.flow.tree'].search([('stages','=','clearing')])
            if type_report == 'enter_clear':
                entry_level = self.env['funds.flow.tree'].search(['|',('stages','=','clearing'),('stages','=','entry')])
            if type_report == 'confirmation':
                entry_level = self.env['funds.flow.tree'].search([('stages','=','confirmation'),('date','>=',form),('date','<=',to)])

            entries = []
            for x in party:
                entries.append(x)

        def opening(party):
            customers = party
            journal_lines= self.env['account.move.line'].search([('partner_id','=',customers.id),('account_id.name','in',["Account Payable","Account Receivable"]),('move_id.state','=',"posted")])

            debit = 0
            credit = 0

            for x in journal_lines:
                debit = debit + x.debit
                credit = credit + x.credit

            opening_balance = debit - credit
            return opening_balance

        record_list = []
        def get_record_list(attr):
            del record_list[:]
            for x in entry_level:
                if x.party == attr:
                    record_list.append(x)
                if x.customer == attr:
                    record_list.append(x)
                if x.supplier == attr:
                    record_list.append(x)

        def getstage(attr):
            if attr == 'entry':
                return 'Entry Level'
            if attr == 'clearing':
                return 'Clearing'
            if attr == 'confirmation':
                return 'Confirmation'

        records = []

        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': records,
            'data': data,
            'entries': entries,
            'opening': opening,
            'get_record_list': get_record_list,
            'record_list': record_list,
            'getreportname': getreportname,
            'getstage': getstage
            }

        return report_obj.render('sugar_reports.funds_recovery', docargs)