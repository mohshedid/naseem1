# -*- coding: utf-8 -*- 
from odoo import models, fields, api

# class custom_model(models.Model):
# 	_name='custom.model'

# 	@api.model
# 	def get_result(self):
# 		return self.get_invoice()

# 	@api.multi
# 	def get_invoice(self):
# 		return {
# 		'type': "ir.actions.act_window",               
# 		'name': "Account Invoice",               
# 		'res_model': "account.invoice",               
# 		'view_type':'form',               
# 		'view_mode':'tree,form',                            
# 		# 'domain' : ([('date_invoice','>',domain)]),		
# 		}