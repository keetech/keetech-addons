# -*- coding: utf-8 -*-
{
    'name': "br_nfce",

    'summary': """
        Módulo para implementação da emissão da NFC-e no Odoo""",

    'description': """
        Módulo para implementação da emissão da NFC-e no Odoo
    """,

    'author': "Raphael Rodrigues <raphael0608@gmail.com>",
    'website': "http://www.deltaos.com.br",

    'category': 'Uncategorized',
    'version': '11.0.0.1',

    'depends': ['base',
                'br_nfe'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],

}