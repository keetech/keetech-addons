# -*- coding: utf-8 -*-
{
    'name': "Funções Extras NF-e",

    'summary': """
        Adiciona funcionalidades extras ao módulo de emissão de Nota Fiscal Eletrônica
        """,

    'description': """
Adiciona funcionalidades extras ao módulo de emissão de Nota Fiscal Eletrônica
==============================================================================

  Funcionalidades Adicionadas

- Impressão da Carta de Correção Eletrônica
- Impressão de Múltiplas DANFEs pela view de Documentos Eletrônicos
    """,

    'author': "Raphael Rodrigues <raphael0608@gmail.com>",
    'website': "http://www.deltaos.com.br",

    'category': 'account',
    'version': '11.0.0.1',

    'depends': ['br_nfe'],
    'auto_install': True,

    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
    ],
}