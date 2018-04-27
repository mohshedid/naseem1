# #-*- coding:utf-8 -*-
# ##############################################################################
# #
# #    OpenERP, Open Source Management Solution
# #    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
# #
# #    This program is free software: you can redistribute it and/or modify
# #    it under the terms of the GNU Affero General Public License as published by
# #    the Free Software Foundation, either version 3 of the License, or
# #    (at your option) any later version.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU Affero General Public License for more details.
# #
# #    You should have received a copy of the GNU Affero General Public License
# #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #
# ##############################################################################
from odoo import models, fields, api

class FundsRecovery(models.Model):
	_name = "funds.recovery"

	to = fields.Date(string="To")
	form = fields.Date(string="From")

	type_report = fields.Selection([
		('clearance','Clearance'),
		('confirmation','Confirmation'),
		('enty_level','Entry Level'),
		('enter_clear','Entry/Clearence')],
		string='Type',default='clearance')
	parties_type = fields.Selection([('all','All'),('specific','Specific')],string='All/Specific',default='all')

	parties = fields.Many2many("res.partner",string="Parties")

class FundRecovery(models.Model):
	_inherit = "funds.flow.tree"    

	@api.model
	def create_report(self):
		return {
		'type': 'ir.actions.act_window',
		'name': 'Funds Recovery',
		'res_model': 'funds.flow.tree',
		'view_type': 'form',
		'view_mode': 'form',
		'target' : 'new',
		}