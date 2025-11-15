# -*- coding: utf-8 -*-
{
    'name': 'TF Finanzas',
    'version': '18.0.1.0',
    'category': 'Sales',
    'summary': 'Custom',
    'description': """
    """,
    'author': 'GRUPO 2',
    'website': '',
    'depends': [
        'base',
        'contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/project_views.xml',
        'views/scenario_simulation_views.xml',
        'views/fee_schedule_line_views.xml',
        'views/financial_product_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}