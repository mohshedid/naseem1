# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SMS_Config(models.TransientModel):
    _inherit = 'base.config.settings'

    user = fields.Char()
    password = fields.Char()
    url = fields.Char()

    @api.multi
    def set_sms_api_user(self):
        user = self[0].user or ''
        self.env['ir.config_parameter'].set_param('user', user)

    @api.multi
    def set_password(self):
        password = self[0].password or ''
        self.env['ir.config_parameter'].set_param('password', password)

    @api.multi
    def set_sms_api_url(self):
        url = self[0].url or ''
        self.env['ir.config_parameter'].set_param('url', url)

    @api.multi
    def get_default_sms_credentials(self, fields=None):
        get_param = self.env['ir.config_parameter'].get_param
        user = get_param('user', default='')
        password = get_param('password', default='')
        url = get_param('url', default='')
        return {
            'user': user,
            'password': password,
            'url' : url
        }