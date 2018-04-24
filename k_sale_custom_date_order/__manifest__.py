# -*- coding: utf-8 -*-
{
    'name': "Customizações Data de Entrega no Módulo de Vendas",

    'summary': """
        Torna obrigatório o campo de data de entrega e modifica a view do Pedido de Vendas""",

    'author': "Raphael Rodrigues <raphael@deltaos.com.br>",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_order_dates',
                'br_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}