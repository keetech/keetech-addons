# -*- coding: utf-8 -*-
# © 2017 Otávio Silveira Munhoz <otaviosilmunhoz@hotmail.com>, ATSTI
# © 2018 Carlos Rodrigues Silveira <crsilveira@gmail.com>, ATSTI
# © 2018 Raphael Rodrigues <raphael0608@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Importação de Documento Fiscal Eletronico de Compras',
    'version': '11.0.1.0.0',
    'category': 'Account Addons',
    'license': 'AGPL-3',
    'author': 'ATSTI',
    'website': 'https://www.atsti.com.br',
    'depends': [
        'purchase',
        'stock',
        'br_purchase',
        'product_reference_sequence',
    ],
    'data': [
        'wizard/import_nfe.xml',
        'wizard/import_nfe_sale.xml',
        'views/purchase_view.xml',
        'views/account_invoice.xml',
    ],
    'auto_install': True,
    'installable': True,
}
