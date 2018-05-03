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


class GeneratePartnerLedger(models.Model):
	_name = "partner.ledger"

	form = fields.Date(string="From")
	to = fields.Date(string="To")
	entry_type = fields.Selection([
		('posted', 'Actual Ledger'),
		('all', 'Virtual Ledger'),
		],default='posted',string="Target Moves")
	partner = fields.Many2one('res.partner',string="Partner",required=True)
	dollar = fields.Boolean(string="Need a Dollar Report")
	pdc = fields.Boolean('Balance With PDC')
	check = fields.Boolean()


	@api.onchange('partner')
	def check_cust(self):
		if self.partner:
			if self.partner.customer == True:
				self.check = True
			if self.partner.supplier == True:
				self.check = False

	

class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	fc_amount = fields.Float(string="Dollar Amount")