# -*- coding: utf-8 -*-

import urllib2

import logging
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class SMS_Template(models.TransientModel):
    _name = 'sms.templates'
    
    to = fields.Char()
    line = fields.Char()
    message = fields.Text()

    @api.onchange('to')
    def onload(self):
        numbers = ''
        active_class =self.env['res.partner'].browse(self._context.get('active_ids'))
        if len(active_class) > 1:
            for rec in active_class:
                if rec.phone != False:
                    numbers = numbers + rec.phone + ','
        else:
            numbers = numbers + active_class.phone
        self.to = numbers

    @api.constrains('message')
    def message_check(self):
        if not self.message:
            raise ValidationError(_('You should have to type some message..'))

    @api.multi
    def send(self):
        get_param = self.env['ir.config_parameter'].get_param
        user = get_param('user', default='')
        password = get_param('password', default='')
        number = self.to
        message = self.message
        message = message.replace(" ", "%20")
        line = self.line
        url = get_param('url', default='')

        if not ',' in number:
            _logger.info(">>>> Sendings sms to number : %s" %(number))
            try:
                urllib2.urlopen(url+'?u=%s&p=%s&l=%s&n=%s&m=%s' %(user,password,1,number,message))
                _logger.info('>>>>>Message sent')
            except Exception as e:
                raise ValidationError(_('Facing error something like : [%s]' %(e)))
        else:
            bulk_numbers = number.split(',')
            len_of_num = len(bulk_numbers)
            for x in range(1,len_of_num):
                if bulk_numbers[x] != '':
                    _logger.info(">>>> Sendings sms to number : %s" %(bulk_numbers[x]))
                    try:
                        urllib2.urlopen(url+'?u=%s&p=%s&l=%s&n=%s&m=%s' %(user,password,1,bulk_numbers[x],message))
                        _logger.info('>>>>>Message sent')
                    except Exception as e:
                        raise ValidationError(_('Facing error something like : [%s]' %(e)))