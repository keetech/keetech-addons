# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from lxml import objectify
import base64

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

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
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['nfe_num'] = self.nfe_num
        res['nfe_serie'] = self.nfe_serie
        res['nfe_modelo'] = self.nfe_modelo
        res['nfe_chave'] = self.nfe_chave
        res['nfe_emissao'] = self.nfe_emissao
        return res        

    @api.multi
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            #import pudb; pu.db
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if partner not in line.product_id.seller_ids.mapped('name') and len(line.product_id.seller_ids) <= 10:
                currency = partner.property_purchase_currency_id or self.env.user.company_id.currency_id
                nfe_string = base64.b64decode(self.xml_purchase)
                nfe = objectify.fromstring(nfe_string)
                for det in nfe.NFe.infNFe.det:
                    price = det.prod.vUnCom
                    total = det.prod.vProd
                    if price == line.price_unit and total == line.price_subtotal:
                        product_code = det.prod.cProd
                        product_name = det.prod.xProd
                supplierinfo = {
                    'name': partner.id,
                    'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                    'product_uom': line.product_uom.id,
                    'product_name': product_name,
                    'product_code': product_code,
                    'min_qty': 0.0,
                    'price': self.currency_id.compute(line.price_unit, currency),
                    'currency_id': currency.id,
                    'delay': 0,
                }
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break