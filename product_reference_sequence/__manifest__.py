# -*- coding: utf-8 -*-
{
    'name': 'Product Sequence',
    'images': ['static/description/main_screenshot.png'],
    'version': '11.0.0.1',
    'summary': 'Generates automatic identifier for product trough a sequence',
    'category': 'Accounting',
    'author': 'Raphael Rodrigues <raphael0608@gmail.com>',
    'website': 'http://www.deltaos.com.br',
    'depends': [
        'base',
        'product',
    ],
    'data': [
        'data/product_sequence.xml',
        'views/views.xml'
    ],
    'auto_install': True,
    'installable': True,
}
