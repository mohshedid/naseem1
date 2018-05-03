# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError

class pdc_bcube(models.Model):
    _name = 'pdc_bcube.pdc_bcube'
    _rec_name = 'nameofrecord'
    _inherit   = ['mail.thread', 'ir.needaction_mixin']

    date = fields.Date('Date Receiving',required=True,default=datetime.now())
    cheque_date = fields.Date('Cheque Date',required=True)
    customer = fields.Many2one('res.partner',string="Customer",required=True)
    sales_person = fields.Many2one('res.users',string="Sales Person",required=True)
    inv_ref = fields.Many2one('account.invoice',string="Invoice Reference")
    days_rem = fields.Char(string="Days Remaining")
    nameofrecord = fields.Char(string="Name",compute="_setRecordName")
    amount =  fields.Float(required=True)
    bank = fields.Many2one('bank.bank',required=True)
    chk_date = fields.Date(string="Check Date",default=date.today())
    chaque_no = fields.Char(string="Cheque No.",required=True)
    account_head = fields.Many2one('account.journal', string="Account Journal")
    pdc_bcube_id = fields.Many2one('pdc_bcube.pdc_bcube')
    pdc_bcube_ids = fields.One2many('pdc_bcube.pdc_bcube','pdc_bcube_id',string="Tree View")
    pdc_cashRegister_ids = fields.One2many('account.bank.statement.line','pdc_cashRegister_id',string="Cash Register")
    remaining_amount = fields.Float(compute="_getRemainingAmount",string="Remaining Amount")
    remaining_balance = fields.Float(compute="_getRemainingBalance",string="Balance")
    stages = fields.Selection([
		('in_hand', 'In Hand'),
        ('deposited', 'Deposited'),
        ('returned', 'Returned'),
        ('settled', 'Settled'),
        ('cancelled', 'Cancelled'),
        ],default='in_hand', track_visibility='onchange')
    # invoice_reference = fields.Many2many('invoice_reference.invoice_reference')
    @api.onchange('cheque_date')
    def days_between(self):
        if self.cheque_date and self.chk_date:
            d1 = datetime.strptime(self.cheque_date, "%Y-%m-%d")
            d2 = datetime.strptime(self.chk_date, "%Y-%m-%d")
            days = abs((d2 - d1).days)
            self.days_rem = str(days)+" "+"Days"
    # Compute Funtion to get remaining amount
    @api.one
    def _getRemainingAmount(self):
        if self.stages == 'settled':
            Amount = 0
            CurrentModelAmount = sum(line.amount for line in self.pdc_bcube_ids)
            if self.pdc_cashRegister_ids:
                CashRegisterAmount = sum(line.amount for line in self.pdc_cashRegister_ids)
                Amount =  CashRegisterAmount
            self.remaining_amount = self.amount - (CurrentModelAmount + Amount)
        else:
            self.remaining_amount = 0
    # Compute Funtion to get remaining Balance
    @api.one
    def _getRemainingBalance(self):
        if self.pdc_bcube_ids:
            CurrentModelAmount = sum(line.amount for line in self.pdc_bcube_ids)
            self.remaining_balance = self.amount - CurrentModelAmount
    # Set Record name 
    @api.one
    def _setRecordName(self):
        self.nameofrecord = '%s /Cheque No.%s/Amount:%s0' %(self.bank.name,self.chaque_no, self.amount)
    # Deposit
    @api.multi
    def genrateJournalEntries(self):
        if self.account_head:
            JornalEntries = self.env['account.move']
            JornalEntries_lines = self.env['account.move.line']
            create_journal_entry = JornalEntries.create({
                    'journal_id': self.account_head.id,
                    'date':self.date,
                    })
            create_journal_entry.line_ids.create({
                'account_id':self.account_head.default_debit_account_id.id,
                'partner_id':self.customer.id,
                'name': 'Debit', 
                'debit':self.amount,
                'move_id':create_journal_entry.id
                })
            create_journal_entry.line_ids.create({
                'account_id':self.customer.property_account_receivable_id.id,
                'partner_id':self.customer.id,
                'name':'Credit',   
                'credit':self.amount,
                'move_id':create_journal_entry.id
                })
            create_journal_entry.post()
            self.write({'stages' : 'deposited'})
        else:
            raise ValidationError('Please Select Account Journal.')
    # Return
    @api.multi
    def returnJournalEntries(self):
        JornalEntries = self.env['account.move']
        JornalEntries_lines = self.env['account.move.line']
        create_journal_entry = JornalEntries.create({
                'journal_id': self.account_head.id,
                'date':self.date,
                })
        create_debit = JornalEntries_lines.create({
            'account_id':self.customer.property_account_receivable_id.id,
            'partner_id':self.customer.id,
            'name': 'Debit', 
            'debit':self.amount,
            'move_id':create_journal_entry.id
            })
        create_credit = JornalEntries_lines.create({
            'account_id':self.account_head.default_debit_account_id.id,
            'partner_id':self.customer.id,
            'name':'Credit',   
            'credit':self.amount,
            'move_id':create_journal_entry.id
            })
        create_journal_entry.post()
        self.write({'stages' : 'returned'})

    # Cancel
    @api.multi
    def cancelJournalEntries(self):
        self.write({'stages' : 'cancelled'})
    # Settle
    @api.multi
    def settleJournalEntries(self):
        self.write({'stages' : 'settled'})


    @api.one
    def unlink(self):
        if self.stages != 'in_hand':
            raise ValidationError('You cannot delete record in this state.')
        return super(pdc_bcube, self).unlink()

class customer_supplie(models.Model):
    _name = 'customer_supplie.customer_supplie'
    name = fields.Char()

class bank(models.Model):
    _name = 'bank.bank'
    name = fields.Char()

class invoice_reference(models.Model):
    _name = 'invoice_reference.invoice_reference'
    name = fields.Char()



class pdc_account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'
    pdc_cashRegister_id = fields.Many2one('pdc_bcube.pdc_bcube')