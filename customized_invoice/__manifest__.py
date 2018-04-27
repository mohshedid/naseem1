# -*- coding: utf-8 -*-
{
    'name': "Professional Invoice & Sales Order Templates",
    'support': 'support@optima.co.ke',

    'summary': """
         Ten professionally designed Invoice & Sales Order templates with multiple settings to customize them""",

    'description': """
        This module will install a customized client invoice report for accounting module.You will be able to customize the invoice colors,logo and the style/format of invoice to look professional and appealing to your customers. You can also create your own template from scratch or edit one of the existing templates that come with this module 
    """,
    'images': ['static/description/invoice.png'],
    'price': 59,
    'currency': 'EUR',


    'author': "Optima ICT Services LTD",
    'website': "http://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'sale_stock'],
    'external_dependencies': {'python': ['num2words','PyPDF2']},
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/res_currency.xml',
        'views/res_partner.xml',
        'views/company_footer.xml',
        'views/company_address.xml',
        'views/company_address_noname.xml',
        'views/category.xml',

        'views/report_style_views.xml',
        'invoice/invoice_lines.xml',
        'invoice/switch_templates.xml',
        'invoice/dl_envelope.xml',
        'invoice/modern_template.xml',
        'invoice/classic_template.xml',
        'invoice/retro_template.xml',
        'invoice/tva_template.xml',
        'invoice/odoo_template.xml',
        'invoice/band_template.xml',
        'invoice/military_template.xml',
        'invoice/western_template.xml',
        'invoice/slim_template.xml',
        'invoice/cubic_template.xml',
        'invoice/clean_template.xml',
        'invoice/account_invoice_view.xml',
        'invoice/invoice_lines_no_layout.xml',

        'sale_order/order_lines.xml',
        'sale_order/switch_templates.xml',
        'sale_order/sale_order_view.xml',
        'sale_order/odoo_template.xml',
        'sale_order/retro_template.xml',
        'sale_order/classic_template.xml',
        'sale_order/tva_template.xml',
        'sale_order/band_template.xml',
        'sale_order/military_template.xml',
        'sale_order/western_template.xml',
        'sale_order/slim_template.xml',
        'sale_order/cubic_template.xml',
        'sale_order/clean_template.xml',
        'sale_order/modern_template.xml',

        'reports/invoice_reports.xml',
        'reports/sale_order_reports.xml',

        'data/res_currency_data.xml',
        'data/default_style.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
