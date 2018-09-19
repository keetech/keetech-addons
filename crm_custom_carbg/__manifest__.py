# -*- coding: utf-8 -*-
{
    'name': "CRM - CARBG Custom",

    'summary': """
        Customizações CRM - Aplicação desenvolvida sob solicitações do cliente""",

    'description': """
        Customizações CRM - Aplicação desenvolvida sob solicitações do cliente""",

    'author': "Raphael Rodrigues <raphael0608@gmail.com>",

    'category': 'CRM',
    'version': '11.0.0.1',

    'depends': ['base', 'crm', 'crm_claim', 'sale'],

    'data': [
        'views/sale_view.xml',
        'views/crm.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
}