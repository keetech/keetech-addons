# -*- coding: utf-8 -*-
{
    'name': "Configurações do Perfil dos Vendedores",

    'summary': """
        Módulo para configuração de perfil de vendedor:
        - Limite de Desconto permitido""",

    'description': """
        Módulo para configuração de perfil de vendedor
    """,

    'author': "Raphael Rodrigues",
    'license': 'AGPL-3',
    'contributors': [
        'Raphael Rodrigues <raphael0608@gmail.com>',
    ],
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sales_team',
                'br_base',
                'br_sale'],

    # always loaded
    'data': [
        'views/salesman.xml',
        'views/sales_discount_approve.xml',
        'views/sale_view.xml',
        'views/templates.xml',
        'security/salesman_security.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'application': True,
}