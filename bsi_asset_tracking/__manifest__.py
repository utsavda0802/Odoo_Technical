{
    'name': 'BSI Asset Tracking',
    'version': '19.0.1.0.0',
    'category': 'Test',
    'summary': 'This is a asset tracking software.',
    'author': 'Botspot Infoware',
    'depends': ['base','mail','hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'views/asset_category_views.xml',
        'views/asset_views.xml',
        'wizards/assign_wizard_views.xml',
        'views/menus.xml',
        'report/asset_report.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}

