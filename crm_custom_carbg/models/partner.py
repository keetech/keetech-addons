# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class ResPartner(models.Model):

    _inherit = "res.partner"

    is_prospect = fields.Boolean(string=u'É um Prospecto', default=False)
    commercial_segment = fields.Selection([('01', u'Alimentos & Bebidas'), ('02', u'Química & Energia'),
                                           ('03', u'Metalurgia'), ('04', u'Manufatura'), ('05', u'Medicinal'),
                                           ('06', u'Eletrônicos'), ('07', u'Distribuidor/Revendedor'),
                                           ('08', u'Outros')])


    @api.onchange('is_prospect')
    def change_prospect(self):
        if self.is_prospect == True:
            self.customer = False

    @api.onchange('customer')
    def change_customer(self):
        if self.customer == True:
            self.is_prospect = False

    # Misc fields
    send_mail = fields.Boolean(string=u'Enviar Email?', default=False)
    dealer = fields.Boolean(string=u'Revendedor', default=False)

    # Informações Estratégicas do Prospecto
    current_supplier = fields.Char(string=u'Fornecedor Atual')
    current_supplier_contract = fields.Boolean(string=u'Possui Contrato?')
    commercial_info = fields.One2many('partner.commercial.info', 'partner_id', auto_join=True,
                                      string=u'Informações Comerciais')
    contract_info = fields.One2many('partner.contract.info', 'partner_id', string=u'Informações de Contratos',
                                    auto_join=True)

    # Vincular produtos da lista de preços ao cliente
    products_id = fields.One2many(related='property_product_pricelist.item_ids', string='Produtos Relacionados',
                                  readonly=True,)

class PartnerCommercialInfo(models.Model):

    _name = 'partner.commercial.info'

    partner_id = fields.Many2one('res.partner', string=u'Cliente / Prospecto', required=True, index=True)
    products = fields.Many2one('product.product', string='Produto', domain=[('sale_ok', '=', True)],
                               ondelete='restrict', required=True)
    application = fields.Char(string="Aplicação")
    price = fields.Float('Preço', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    volume = fields.Char(string=u'Volume')

class PartnerContractInfo(models.Model):

    _name = 'partner.contract.info'

    partner_id = fields.Many2one('res.partner', string=u'Cliente / Prospecto', required=True, index=True)
    products = fields.Many2many('product.product', string=u'Produtos')
    internal_ref = fields.Char(string=u'Código do Contrato')
    date_start = fields.Date(string=u'Data Inicial')
    date_end = fields.Date(string=u'Data Final')
    contract_term = fields.Char(string=u'Prazo Contratual')
    deadline_complaint = fields.Char(string=u'Prazo de Denúncia')
    date_complaint = fields.Date(string=u'Fim do Prazo de Denúncia')
    lending_istrue = fields.Boolean(string=u'Comodato?')