# -*- coding: utf-8 -*-
{
    'name': "CRM Birthday Partner",

    'summary': """
        Adiciona o campo data de aniversário aniversário ao Parceiro""",

    'description': """
        Adiciona o campo data de aniversário aniversário ao Parceiro
    """,

    'author': "Raphael Rodrigues <raphael0608@gmail.com>",

    'category': 'CRM',
    'version': '11.0.0.1',

    'depends': ['base',
                'crm'],

    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
}