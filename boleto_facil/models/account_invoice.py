# -*- coding: utf-8 -*-
# © 2018 Raphael Rodrigues, <raphael@deltaos.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
import BoletoFacil

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def gerar_boleto_facil(self):
        '''Função para Gerar Boleto no Boleto Fácil'''
        description = ''
        for line in self.order_line:
            description += '- %s \n' %(line.name)
        cobranca = {
            'payerName': self.partner_id.name,
            'payerCpfCnpj': self.partner_id.cnpj_cpf,
            'description': description,
            'dueDate': self.date_due,
            'amount': self.amount_total,
            'reference': self.number,
        }
