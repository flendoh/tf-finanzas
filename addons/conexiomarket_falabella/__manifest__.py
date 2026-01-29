{
    'name': 'Conexio Market - Falabella Base',
    'version': '18.0.1.0.0',
    'summary': 'Base module for Falabella integration',
    'description': """
        Base module for Falabella integration.
        Contains credentials and general configuration.
    """,
    'category': 'Integration',
    'author': 'mhallasi',
    'depends': ['conexiomarket_core'],
    'data': [
        'views/market_account_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
