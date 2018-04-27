# -*- coding: utf-8 -*-
{
    'name': "Glare SMS Services",

    'summary': """
        Send Single and Bulk SMS to Targets""",
    'description': """
        Send Single and Bulk SMS to Targets
    """,
    'author': "Wahab Ali Malik",
    'website': "http://www.glareerp.com",
    'version': '0.1',
    'depends': ['base','mail','contacts'],
    'data': [
        'views/config.xml',
        'views/sms_template.xml',
    ],
}