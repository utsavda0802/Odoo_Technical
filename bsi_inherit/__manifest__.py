{
	'name':'Custom Sale Invoice Fields Practice',
	'version':'19.0.1.0.0',
	'summary':'Learnig module for inheritance xpath and super',
	'category':'Sales',
	'depends':['sale','account'],
	'data':[
		'views/sale_order_views.xml',
		'views/account_move_views.xml',
		'report/sale_report_templates.xml',
		'report/invoice_report_templates.xml',
	],
	'license': 'OPL-1',
    'installable': True,
    'application': True,
}