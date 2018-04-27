# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EcubeReceiptEMail(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        res = super(EcubeReceiptEMail, self).post()
        if self.journal_id.code == "BNK2":
	        template = self.env.ref('ecube_receipt_email.ecube_receipt_email_template')
	        self.env['mail.template'].browse(template.id).send_mail(self.id)
        return res