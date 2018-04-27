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
import time


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
            supp = " "
            supplier = self.env['stock.history'].search([(('product_id.id','=',attr))])
            for x in supplier:
                last.append(x)
                newlist = sorted(last, key=lambda x: x.date)
                name = newlist.pop().date
            for x in supplier:
                if x.date == name:
                    for y in x.move_id:
                        for z in y.picking_id:
                            supp = z.partner_id.name

            return supp


        def get_time():
            t0 = time.time()
            t1 = t0 + (60*60)*5 
            new = time.strftime("%I:%M",time.localtime(t1))

            return new


        docargs = {
            'doc_ids': docids,
            'doc_model': 'product.product',
            'docs': records,
            'data': data,
            'hand': hand,
            'get_supp': get_supp,
            'get_time': get_time,

            }

        return report_obj.render('product_reorder_list.module_report', docargs)