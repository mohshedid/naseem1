# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta

class pdc_bcube(models.Model):
    _name = 'pdc_bcube.pdc_bcube'
    _rec_name = 'chaque_no'

    date = fields.Date('Date Receiving')
    cheque_date = fields.Date('Cheque Date')
    customer = fields.Many2one('res.partner',string="Customer",required=True)
    inv_ref = fields.Many2one('account.invoice',string="Invoice Reference")
    days_rem = fields.Char(string="Days Remaining")
    amount =  fields.Float()
    bank = fields.Many2one('bank.bank')
    chk_date = fields.Date(string="Check Date",default=date.today())
    chaque_no = fields.Char(string="Cheque No.")
    stages = fields.Selection([
		('in_hand', 'In Hand'),
        ('deposited', 'Deposited'),
        ('credited', 'Credited'),
        ('returned', 'Returned'),
        ('settled', 'Settled'),
        ('swap', 'Swap'),
        ('cancelled', 'Cancelled'),
        ],default='in_hand')
    # invoice_reference = fields.Many2many('invoice_reference.invoice_reference')
    @api.onchange('cheque_date')
    def days_between(self):
        if self.cheque_date:
            d1 = datetime.strptime(self.cheque_date, "%Y-%m-%d")
            d2 = datetime.strptime(self.chk_date, "%Y-%m-%d")
            days = abs((d2 - d1).days)
            self.days_rem = str(days)+" "+"Days"

class customer_supplie(models.Model):
    _name = 'customer_supplie.customer_supplie'
    name = fields.Char()

class bank(models.Model):
    _name = 'bank.bank'
    name = fields.Char()

class invoice_reference(models.Model):
    _name = 'invoice_reference.invoice_reference'
    name = fields.Char()