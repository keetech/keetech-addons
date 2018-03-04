# -*- coding: utf-8 -*-
{
    'name': "br_pos",

    'summary': """
        Módulo Ponto de Vendas conforme exigências brasileiras.""",

    'description': """
        Módulo Ponto de Vendas conforme exigências brasileiras.
    """,

    'author': "Raphael Rodrigues <raphael0608@gmail.com>",
    'website': "http://www.deltaos.com.br",

    'category': 'Point of Sales',
    'version': '11.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'pos',
                'br_nfe',],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
}