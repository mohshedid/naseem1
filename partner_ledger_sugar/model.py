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
from openerp.exceptions import Warning

class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.partner_ledger_sugar.partner_ledger_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('partner_ledger_sugar.partner_ledger_report')
        active_wizard = self.env['partner.ledger'].search([])
        records = self.env['res.partner'].browse(docids)
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['partner.ledger'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['partner.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        typed = record_wizard.entry_type
        partner_wiz = record_wizard.partner
        dollar = record_wizard.dollar
        pdc = record_wizard.pdc


        def typing():
            if typed == "all":
                return "Virtual"

            if typed == "posted":
                return "Actual"

        if typed == "all":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('partner_id.id','=',record_wizard.partner.id),'|',('account_id.user_type_id','=','Receivable'),('account_id.user_type_id','=','Payable')])

        if typed == "posted":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('partner_id','=',record_wizard.partner.id),'|',('account_id.user_type_id','=','Receivable'),('account_id.user_type_id','=','Payable'),('move_id.state','=',"posted")])

        if typed == "all":
            entred = self.env['account.move.line'].search([('move_id.date','<',form),('partner_id.id','=',record_wizard.partner.id),'|',('account_id.user_type_id','=','Receivable'),('account_id.user_type_id','=','Payable')])

        if typed == "posted":
            entred = self.env['account.move.line'].search([('move_id.date','<',form),('partner_id','=',record_wizard.partner.id),'|',('account_id.user_type_id','=','Receivable'),('account_id.user_type_id','=','Payable'),('move_id.state','=',"posted")])

        if dollar == False:
            debits = 0
            credits = 0
            for x in entred:
                debits = debits + x.debit
                credits = credits + x.credit

            opening_bal = debits - credits

        if dollar == True:
            debits = 0
            credits = 0
            for x in entred:
                if x.debit > 0:
                    debits = debits + x.fc_amount

                if x.credit > 0:
                    credits = credits + x.fc_amount

            opening_bal = debits - credits

        pdc = self.env['pdc_bcube.pdc_bcube'].search([('customer','=',record_wizard.partner.id)])

        def pdc_check():
            num = 0
            if record_wizard.pdc:
                num = 1
            else:
                num = 0

            return num
            
        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': records,
            'data': data,
            'form': form,
            'to': to,
            'typed': typed,
            'entries': entries,
            'opening_bal': opening_bal,
            'partner_wiz': partner_wiz,
            'typing': typing,
            'dollar': dollar,
            'pdc': pdc,
            'pdc_check': pdc_check,
        }

        return report_obj.render('partner_ledger_sugar.partner_ledger_report', docargs)