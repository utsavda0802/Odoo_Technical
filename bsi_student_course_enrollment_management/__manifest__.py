{
    'name': 'BSI Student Course Enrollment Management',
    'version': '19.0.1.0.0',
    'category': 'Test',
    'summary': 'This is a student course enrollment management software.',
    'author': 'Botspot Infoware',
    'depends': ['base','website'],
    'data': [
        'security/ir.model.access.csv',

        # Wizard files
        'wizard/update_students_wizard_views.xml',
        'wizard/manage_sessions_wizard_views.xml',

        # Other wizard files
        'wizard/create_course_wizard_views.xml',
        'wizard/enroll_student_wizard_views.xml',
        'wizard/replace_wizard_views.xml',

        # Main views
        'views/course_views.xml',
        'views/student_views.xml',
        'views/menu.xml',
        'views/student_template.xml',
        'views/student_detail_template.xml',
        'views/student_edit_template.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}
