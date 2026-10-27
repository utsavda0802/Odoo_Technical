{
    'name': 'BSI Employee Test Answer',
    'version': '19.0.1.0.0',
    'category': 'Test',
    'summary': 'This is a employee test answer solving',
    'author': 'Botspot Infoware',
    'depends': ['base',],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',

        'views/employee_views.xml',
        'views/department_views.xml',

        'wizard/salary_revision_wizard_views.xml',
        'report/employee_report.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}


