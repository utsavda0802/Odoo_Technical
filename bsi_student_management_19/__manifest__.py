{
    'name': 'Student Management System',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Manage Student Records',
    'author': 'Botspot Info.',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/student_views.xml',
        'views/std_views.xml',
        'views/teacher_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}