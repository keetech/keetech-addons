# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# © 2018 Raphael Rodrigues, Delta Open Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{   # pylint: disable=C8101,C8103
    'name': 'Pagamento de Comissões',
    'description': "Pagamento de Royalties",
    'summary': "Pagamento de Royalties",
    'version': '11.0.1.0.0',
    'category': "account",
    'author': 'Raphael Rodrigues',
    'license': 'AGPL-3',
    'website': '',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>',
        'Raphael Rodrigues <raphael0608@gmail.com>',
    ],
    'depends': [
        'product',
        'sale',
        'account',
        'account_voucher',
    ],
    'data': [
        'views/product.xml',
        'views/res_partner.xml',
        'views/royalties.xml',
        'views/account_voucher.xml',
        'views/fiscal_position.xml',
        'views/account_journal.xml',
        'wizard/royalties.xml',
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
