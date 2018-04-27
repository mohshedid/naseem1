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
import time
import re 
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning


class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.balance_sheet_turkina.module_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('balance_sheet_turkina.module_report')
        active_wizard = self.env['ecube.balance.sheet'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['ecube.balance.sheet'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['ecube.balance.sheet'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        state = record_wizard.state
        form = record_wizard.form
        to = record_wizard.to
        report_name = record_wizard.name.name

        records = self.env['ecube.report.structure'].search([('description','=',state),('name','=',report_name)])
        
        sequenced = []
        iterations = []

        for x in records.report_link:
            sequenced.append(x.sequence)
        sequenced.sort()

        for x in sequenced:
            for y in records.report_link:
                if x == y.sequence:
                    iterations.append(y)

        report_heads = []
        divisions = []

        def getcurr():
            company = self.env['res.company'].search([('name','=','Turkina Trading')])
            print company.currency_id.symbol
            print "--------------------------"
            return company.currency_id.symbol


        def genrate_values():

            current_records_del = records.division_link
            current_records_del.unlink()

            del report_heads[:]
            del divisions[:]

            active_report = self.env['ecube.report.structure'].search([('description','=',state),('name','=',report_name)])
            division_lines = self.env['ecube.report.structure.divisions'].search([])

            for x in active_report.report_link:
                report_heads.append(x)

            if active_report.division:
                for x in active_report.division:
                    divisions.append(x.name)

                for a in report_heads:
                    head_total = 0
                    if a.entry_type != 'heading':

                        if a.entry_type == 'account':

                            for b in divisions:

                                credit = 0
                                debit = 0
                                total = 0

                                baranch_accounts = self.env['account.move'].search([('branch', '=', b)])
                                
                                for c in a.account_head:

                                    account = []
                                    for d in baranch_accounts:

                                        for e in d.line_ids:
                                                            
                                            if e.account_id.id == c.id:
                                                account.append(e)

                                    for f in account:
                                        credit = credit + f.credit
                                        debit = debit + f.debit

                                nature = a.nature

                                if nature == 'debit':
                                    total = debit - credit
                                
                                if nature == 'credit':
                                    total = credit - debit

                                head_total = head_total + total
                                a.amount = head_total
                                create_division_lines= division_lines.create({
                                    'report_id': a.id,
                                    'description': a.description.id,
                                    'partner': b,
                                    'amount': total,
                                    'divisions_tree': active_report.id,
                                })

                        if (a.entry_type == 'total' or a.entry_type == 'grand_total'):
                            formula = []
                            if a.summary2:
                                formulaie = a.summary2
                                splition = re.split('; |, |\*|-|\+|\/',formulaie)

                                address = 0
                                for b in formulaie:
                                    if (b == '/' or b == '+' or b == '-' or b == '*'):
                                        formula.append(splition[address])
                                        formula.append(b)
                                        address = address + 1

                                formula.append(splition[address])

                                totaler = 0
                                for c in active_report.division:

                                    total_of_partner = 0
                                    symbol = ' '
                                    for d in formula:
                                        if (d != '+' and d != '-' and d != '*' and d != '/'):
                                            divisioned = self.env['ecube.report.structure.divisions'].search([('report_id','=',d),('partner','=',c.name)])
                                            if total_of_partner == 0:
                                                total_of_partner = divisioned.amount
                                            else:
                                                if symbol == '+':
                                                    total_of_partner = total_of_partner + divisioned.amount
                                                elif symbol == '-':
                                                    total_of_partner = total_of_partner - divisioned.amount
                                                elif symbol == '*':
                                                    total_of_partner = total_of_partner * divisioned.amount
                                                elif symbol == '/':
                                                    total_of_partner = total_of_partner / divisioned.amount
                                        else:
                                            symbol = d

                                    totaler = totaler + total_of_partner
                                    create_division_lines= division_lines.create({
                                        'report_id': a.id,
                                        'description': a.description.id,
                                        'partner': c.name,
                                        'amount': total_of_partner,
                                        'divisions_tree': active_report.id,
                                    })

                                a.amount = totaler

            if not (active_report.division):

                for a in report_heads:
                    head_total = 0
                    credit = 0
                    debit = 0
                    total = 0
                    if a.entry_type != 'heading':

                        if a.entry_type == 'account':

                            baranch_accounts = self.env['account.move'].search([])
                                
                            for c in a.account_head:

                                account = []
                                for d in baranch_accounts:

                                    for e in d.line_ids:
                                                        
                                        if e.account_id.id == c.id:
                                            account.append(e)

                                for f in account:
                                    credit = credit + f.credit
                                    debit = debit + f.debit

                            nature = a.nature

                            if nature == 'debit':
                                total = debit - credit
                            
                            if nature == 'credit':
                                total = credit - debit

                            head_total = head_total + total
                            a.amount = head_total

                        if (a.entry_type == 'total' or a.entry_type == 'grand_total'):
                            formula = []
                            if a.summary2:
                                formulaie = a.summary2
                                splition = re.split('; |, |\*|-|\+|\/',formulaie)

                                address = 0
                                for b in formulaie:
                                    if (b == '/' or b == '+' or b == '-' or b == '*'):
                                        formula.append(splition[address])
                                        formula.append(b)
                                        address = address + 1

                                formula.append(splition[address])

                                totaler = 0

                                symbol = ' '
                                for d in formula:
                                    if (d != '+' and d != '-' and d != '*' and d != '/'):
                                        divisioned = self.env['ecube.report.structure.details'].search([('id','=',d)])
                                        if totaler == 0:
                                            totaler = divisioned.amount
                                        else:
                                            if symbol == '+':
                                                totaler = totaler + divisioned.amount
                                            elif symbol == '-':
                                                totaler = totaler - divisioned.amount
                                            elif symbol == '*':
                                                totaler = totaler * divisioned.amount
                                            elif symbol == '/':
                                                totaler = totaler / divisioned.amount
                                    else:
                                        symbol = d

                                a.amount = totaler

        
        def head_total_(attr,partner):
            divisioned = self.env['ecube.report.structure.divisions'].search([('report_id','=',attr),('partner','=',partner)])

            return divisioned.amount

        def other_report(attr,partner):
            divisioned = self.env['ecube.report.structure.divisions'].search([('report_id','=',attr),('partner','=',partner)])
            all_reports = self.env['ecube.report.structure'].search([]) 

            search_id = divisioned.summary2

            for x in all_reports:
                for y in all_reports.division_link:
                    if (y.report_id == search_id and y.partner == partner):
                        return y.amount

        def call_heading():
            if state == 'balance_sheet':
                return "Balance Sheet"
                
            if state == 'profit_loss':
                return "Profit and Loss"
                
            if state == 'cash':
                return "Cash Flow"
            
        docargs = {
            'doc_ids': docids,
            'doc_model': 'ecube.report.structure',
            'docs': records,
            'data': data,
            'other_report': other_report,
            'head_total_': head_total_,
            'form': form,
            'to': to,
            'call_heading': call_heading,
            'genrate_values': genrate_values,
            'iterations': iterations,
            'getcurr': getcurr
        }

        return report_obj.render('balance_sheet_turkina.module_report', docargs)