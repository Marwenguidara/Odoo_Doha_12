{
    'name': "Drawing Service",

    'summary': """Items of Projects""",

    'description': """this module is for estimate and manage projects in doha """,

    'author': "Wassim Guesmi",
    'website': "http://five-consulting.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Construction management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'product',
                'mail',
                'project',
                'mail',
                'survey',
                'estimation'],
    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/drawing.xml',
        'views/item_number.xml',
        'views/item_stage.xml',
        'views/item_code.xml',
        'views/sub_item.xml',
        'views/inherit_project.xml',
        'report/boq_report.xml',
        'report/quotation_report.xml',
        'report/report.xml',
        'data/mail_template.xml',
        'data/stage_data.xml',
        'views/menu_view.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}