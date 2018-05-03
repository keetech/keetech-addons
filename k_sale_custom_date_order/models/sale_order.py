import re
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    """Add several date fields to Sales Orders, computed or user-entered"""
    _inherit = 'sale.order'

    requested_date = fields.Datetime('Requested Date', readonly=True, states={'draft': [('readonly', False)],
                                                                              'sent': [('readonly', False)],
                                                                              'sale': [('readonly', False),
                                                                                       ('required', True)]},
                                     copy=False,
                                     help="Date by which the customer has requested the items to be "
                                          "delivered.\n"
                                          "When this Order gets confirmed, the Delivery Order's "
                                          "expected date will be computed based on this date and the "
                                          "Company's Security Delay.\n"
                                          "Leave this field empty if you want the Delivery Order to be "
                                          "processed as soon as possible. In that case the expected "
                                          "date will be computed using the default method: based on "
                                          "the Product Lead Times and the Company's Security Delay.")


    @api.multi
    def sale_order_pre_validation(self):
        errors = []
        if self.fiscal_position_id.product_document_id.electronic:
            for line in self.order_line:
                if not line.product_id.fiscal_classification_id:
                    errors.append(
                        u'O produto ( %s ) não possui NCM, por favor corrija o cadastro do produto.' %(line.name))
                if not line.product_id.default_code:
                    errors.append(
                        u'O produto ( %s ) não possui Código, por favor corrija o cadastro do produto.' % (line.name))
            if not self.partner_id.cnpj_cpf:
                errors.append(u'Cadastro do cliente não possui CNPJ/CPF.')
            if self.partner_id.company_type == 'company' and not self.partner_id.legal_name:
                errors.append(u'Cadastro do cliente não possui Razão Social')
            if not self.partner_id.street:
                errors.append(u'Cadastro do cliente não possui Endereço - Logradouro')
            if not self.partner_id.number:
                errors.append(u'Cadastro do cliente não possui Endereço - Número')
            if not self.partner_id.zip or len(
                    re.sub(r"\D", "", self.partner_id.zip)) != 8:
                errors.append(u'Cadastro do cliente não possui Endereço - CEP')
            if not self.partner_id.state_id:
                errors.append(u'Cadastro do cliente não possui Endereço - Estado')

            if self.partner_id.state_id:
                if not self.partner_id.state_id.ibge_code:
                    errors.append(u'Cadastro do cliente não possui Endereço - Código do IBGE \
                                                  do estado')
                if not self.partner_id.state_id.name:
                    errors.append(u'Cadastro do cliente não possui Endereço - Nome do estado')

            if not self.partner_id.city_id:
                errors.append(u'Cadastro do cliente não possui Endereço - Município')

            if self.partner_id.city_id:
                if not self.partner_id.city_id.name:
                        errors.append(u'Cadastro do cliente não possui Endereço - Nome do \
                                                  município')
                if not self.partner_id.city_id.ibge_code:
                        errors.append(u'Cadastro do cliente não possui Endereço - Código do IBGE \
                                                  do município')
            if not self.partner_id.country_id:
                errors.append(u'Cadastro do cliente não possui Endereço - País')

        if not self.partner_id.property_account_position_id:
            errors.append(u'É necessário informar a Posição Fiscal do cliente para confirmar a Venda.')

        return errors

    @api.multi
    def action_confirm(self):
        if not self.requested_date:
            raise UserError("Para confirmar a venda por favor insira uma data de entrega.")
        errors = self.sale_order_pre_validation()
        if len(errors) > 0:
            msg = u"\n".join(
                [u"Para confirmar o Pedido corrija os erros abaixo:"] + errors)
            self.unlink()
            raise UserError(msg)

        return super(SaleOrder, self).action_confirm()