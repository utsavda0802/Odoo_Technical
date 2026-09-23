{
    'name': 'BSI Custom Sale_Purchase',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'This is custom project with custom sale and purchase functionality. ',
    'author': 'Botspot Infoware',
    'depends': ['base','sale_management','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/gst_form_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}