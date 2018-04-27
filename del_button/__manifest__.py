{
    'name': 'Delete Button On Customer Invoices',
    'version': '1.0',
    'category': 'General',
    'summary': 'Delete Button On Customer Invoices',
    'description': """ Delete Button On Customer Invoices """,
    'author': 'Muhammad Mian Kamran ,Ehtisham Faisal',
    'website': 'http://www.ecube.pk',
    'depends': ['base','purchase','web','sale','product'],
    'data':[
            'views/tree_view_asset.xml',
            ],
    'qweb': ['static/src/xml/tree_view_button.xml'], 
    'js': 'static/src/js/tree_view_button.js',      
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}