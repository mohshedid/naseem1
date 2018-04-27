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
    _name = 'report.mr_fabrics_plan.module_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('mr_fabrics_plan.module_report')
        records = self.env['res.partner'].browse(docids)


        # enteries = []
        # for x in records.sum_ids:
        #     enteries.append(x)


        # region = []
        # for x in enteries:
        #     if x.Region not in region:
        #         region.append(x.Region)
        # region.sort(key=int)
        
       
        # sorted_records = []
        # for x in region:
        #     for y in enteries:
        #         if y.Region == x:
        #             sorted_records.append(y)


      

        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': records,
            'data': data
            # 'enteries': enteries
            # 'sorted_records': sorted_records
            }

        return report_obj.render('mr_fabrics_plan.module_report', docargs)