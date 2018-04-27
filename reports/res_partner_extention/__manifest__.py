# -*- coding: utf-8 -*-
{
    'name': "res_partner_extention",

    'summary': """
        All Res Partner Class Extentions In This Module""",

    'description': """
        All Res Partner Class Extentions In This Module
    """,

    'author': "Bcube",
    'website': "http://www.oxenlab.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product_naseem'],

    # always loaded
    'data': [
        'views/res_partner_templates.xml',
    ],
}