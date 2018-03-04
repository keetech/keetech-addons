# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    nfe_num = fields.Integer('Num. NFe')
    nfe_serie = fields.Char('Série')
    nfe_modelo = fields.Char('Modelo')
    nfe_chave =  fields.Char('Chave NFe')
    nfe_emissao = fields.Date('Data Emissão NFe')
    xml_purchase = fields.Binary(string=u"Xml da NFe", readonly=True)
    xml_name = fields.Char(string=u'Xml da NFe de compra', readonly=True)

    @api.multi
    def _prepare_invoice(self):
        import pudb;pu.db
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['nfe_num'] = self.nfe_num
        res['nfe_serie'] = self.nfe_serie
        res['nfe_modelo'] = self.nfe_modelo
        res['nfe_chave'] = self.nfe_chave
        res['nfe_emissao'] = self.nfe_emissao
        return res        
