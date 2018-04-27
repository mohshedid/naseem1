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
from datetime import datetime,date


class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.product_reorder_list.module_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_reorder_list.module_report')
        records = self.env['product.product'].browse(docids)

        def hand(attr):
            amt = 0
            data = self.env['stock.history'].search([])
            for x in data:
                if attr == x.product_id.id:
                    amt = amt + x.quantity

            return amt
            

        def get_supp(attr):
            last = []
            name = " "
            supplier = self.env['account.invoice'].search([(('type','=',"in_invoice"))])
            for x in supplier:
                if x.invoice_line_ids.product_id.id == attr:
                    last.append(x)
                    newlist = sorted(last, key=lambda x: x.id)
                    name = newlist.pop().partner_id.name


            return name


        docargs = {
            'doc_ids': docids,
            'doc_model': 'product.product',
            'docs': records,
            'data': data,
            'hand': hand,
            'get_supp': get_supp,

            }

        return report_obj.render('product_reorder_list.module_report', docargs)