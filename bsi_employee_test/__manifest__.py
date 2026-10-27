{
    'name': 'BSI Employee Test',
    'version': '19.0.1.0.0',
    'category': 'Test',
    'summary': 'This is a employee test ',
    'author': 'Botspot Infoware',
    'depends': ['base',],
    'data': [
        'data/sequence_data.xml',
        'report/employee_report_actions.xml',
        'report/employee_report_template.xml',
        'security/ir.model.access.csv',
        'views/employee_views.xml',
        'wizards/increase_salary_wizard.xml'
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}