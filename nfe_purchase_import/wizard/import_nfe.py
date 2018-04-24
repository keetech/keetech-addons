# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini <alessandrofmartini@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64

from lxml import objectify
from dateutil import parser
from random import SystemRandom
from datetime import  datetime

from odoo import api, models, fields
from odoo.exceptions import UserError


class WizardImportNfe(models.TransientModel):
    _name = 'wizard.import.nfe'

    nfe_xml = fields.Binary(u'XML da NFe')
    fiscal_position_id = fields.Many2one('account.fiscal.position',
                                         string='Posição Fiscal')
    payment_term_id = fields.Many2one('account.payment.term',
                                      string='Forma de Pagamento')
    not_found_product = fields.Many2many('not.found.products', string="Produtos não encontrados")
    confirma = fields.Boolean(string='Confirmado?')


    def retorna_data(self, nfe):
        ide = nfe.NFe.infNFe.ide
        day = str(ide.dhEmi).split('T')
        hour = day[1].split('-')
        datehour = day[0] + ' ' + hour[0]
        datetime_obj = datetime.strptime(datehour, '%Y-%m-%d %H:%M:%S')
        return datetime_obj

    def arruma_cpf_cnpj(self, partner_doc):
        if len(partner_doc) > 11:
            if len(partner_doc) < 14:
                partner_doc = partner_doc.zfill(14)
            partner_doc = "%s.%s.%s/%s-%s" % ( partner_doc[0:2], partner_doc[2:5], partner_doc[5:8], partner_doc[8:12], partner_doc[12:14] )
        else:
            if len(partner_doc) < 11:
                partner_doc = partner_doc.zfill(11)
            partner_doc = "%s.%s.%s-%s" % (partner_doc[0:3], partner_doc[3:6], partner_doc[6:9], partner_doc[9:11])
        return partner_doc

    def get_main_purchase(self, nfe):
        #ide = nfe.NFe.infNFe.ide
        num_nfe = nfe.NFe.infNFe.ide.nNF
        chave = nfe.protNFe.infProt.chNFe
        emit = nfe.NFe.infNFe.emit
        partner_doc = emit.CNPJ.text if hasattr(emit, 'CNPJ') else stremit.CPF.text
        partner_doc = str(partner_doc)
        partner_doc = self.arruma_cpf_cnpj(partner_doc)
        partner = self.env['res.partner'].search([
            ('cnpj_cpf', '=', partner_doc)])
        if not partner:
            raise UserError('Fornecedor não encontrado, por favor, crie um fornecedor com CPF/CNPJ igual a ' + partner_doc)
        order = self.env['purchase.order'].search([
            ('partner_id', '=', partner.id),
            ('partner_ref', '=', num_nfe)
        ])
        if order:
            raise UserError('Nota já importada')

        datetime_obj = self.retorna_data(nfe)
        return dict(
            partner_id=partner.id,
            date_planned=datetime_obj,
            date_order=datetime_obj,
            payment_term_id=self.payment_term_id.id,
            fiscal_position_id=self.fiscal_position_id.id,
            partner_ref=num_nfe,
            nfe_num=num_nfe,
            nfe_emissao=datetime_obj,
            nfe_serie = nfe.NFe.infNFe.ide.serie,
            nfe_modelo= nfe.NFe.infNFe.ide.mod,
            nfe_chave = chave,
        )

    def create_order_line(self, item, nfe, order_id):
        #import pudb; pu.db
        emit = nfe.NFe.infNFe.emit
        partner_doc = emit.CNPJ if hasattr(emit, 'CNPJ') else emit.CPF
        partner_id = self.env['res.partner'].search([('cnpj_cpf', '=', self.arruma_cpf_cnpj(str(partner_doc)))]).id
        uom_id = self.env['product.uom'].search([
            ('name', '=', str(item.prod.uCom))], limit=1).id
        product = self.env['product.product'].search([
            ('default_code', '=', item.prod.cProd)], limit=1)
        if not product:
            product = self.env['product.product'].search([
                ('barcode', '=', item.prod.cEAN)], limit=1)
        if not product:
            product_code = self.env['product.supplierinfo'].search([
                ('supplier_code', '=', item.prod.cProd), ('name', '=', partner_id)
            ])
            product = self.env['product.product'].browse(product_code.product_tmpl_id.id)

        if not product:
            if self.not_found_product:
                for line in self.not_found_product:
                    if line.name == item.prod.xProd:
                        if line.product_id:
                            product = self.env['product.product'].browse(line.product_id.id)
                            '''
                            Se os produtos não forem encontrados você pose
                            informa-los através do wizard
                            '''
                            prd_ids = {}
                            prd_ids['product_id'] = line.product_id.id
                            prd_ids['product_tmpl_id'] = line.product_id.product_tmpl_id.id
                            prd_ids['name'] = partner_id
                            prd_ids['product_name'] = str(item.prod.xProd)
                            #prd_ids['product_code'] = str(item.prod.cProd)
                            self.env['product.supplierinfo'].create(prd_ids)
                            break
                        else:
                            '''
                            Caso os produtos não sejam encontrados no sistema
                            e você não os informe no wizard, eles serão cadastrados
                            automaticamente utilizando as informações contidas no XML
                            '''
                            vals = {}
                            vals['name'] = str(item.prod.xProd)
                            if uom_id:
                                vals['uom_id'] = uom_id
                            else:
                                vals['uom_id'] = 1
                            vals['type'] = 'product'
                            vals['list_price'] = float(item.prod.vUnCom)
                            vals['purchase_method'] = 'receive'
                            vals['tracking'] = 'none'
                            ncm = str(item.prod.NCM)
                            pf_ids = self.env['product.fiscal.classification'].search([('code', '=', ncm)])
                            vals['fiscal_classification_id'] = pf_ids.id
                            product = self.env['product.product'].create(vals)
                            # o codigo do produto sera gerado atraves do sequencial
                            #category = product.categ_id
                            #product.default_code = category.get_next_id()
                            break
        product_id = product.id
        quantidade = item.prod.qCom
        preco_unitario = item.prod.vUnCom
        discount = item.prod.vDesc if hasattr(item.prod, 'vDesc') else 0.0
        #if item.prod.vDesc:
        #    discount = item.prod.vDesc
        datetime_obj = self.retorna_data(nfe)
        return self.env['purchase.order.line'].create({
            'product_id': product_id,'name':product.name,'date_planned':datetime_obj,
            'product_qty': quantidade, 'price_unit': preco_unitario, 'valor_desconto': discount,
            'product_uom':product.uom_id.id, 'order_id':order_id,'partner_id':partner_id
        })

    def get_items_purchase(self, nfe, order_id):
        items = []
        for det in nfe.NFe.infNFe.det:
            item = self.create_order_line(det, nfe, order_id)
            items.append((4, item.id, False))
        return {'order_line': items}

    @api.multi
    def action_import_nfe_purchase(self):
        if not self.nfe_xml:
            raise UserError('Por favor, insira um arquivo de NFe.')
        nfe_string = base64.b64decode(self.nfe_xml)
        nfe = objectify.fromstring(nfe_string)
        purchase_dict = {}
        purchase_dict.update(self.get_main_purchase(nfe))
        order = self.env['purchase.order'].create(purchase_dict)
        order.xml_purchase = self.nfe_xml
        order.xml_name = "NFe-Compra-%08d.xml" % purchase_dict['nfe_num']
        purchase_dict = {}
        order_id = order.id
        purchase_dict.update(self.get_items_purchase(nfe, order_id))
        order.write(purchase_dict)
        order._compute_tax_id()

    def carrega_produtos(self, item, nfe):
        #product = self.env['product.product'].search([
        #    ('default_code', '=', item.prod.cProd)], limit=1)
        #if not product:
        product = self.env['product.product'].search([
                ('barcode', '=', item.prod.cEAN)], limit=1)
        #if not product:
        #    product = self.env['product.product'].search([
        #        ('barcode', '=', item.prod.cEAN)], limit=1)
        if not product:
            emit = nfe.NFe.infNFe.emit
            partner_doc = emit.CNPJ.text if hasattr(emit, 'CNPJ') else emit.CPF
            partner_id = self.env['res.partner'].search([('cnpj_cpf', '=', self.arruma_cpf_cnpj(str(partner_doc)))]).id
            product_code = self.env['product.supplierinfo'].search([
                ('product_code','=',item.prod.cProd),
                ('name','=',partner_id)
            ], limit=1)
            product = self.env['product.product'].browse(product_code.product_tmpl_id.id)
        if not product:
            return self.env['not.found.products'].create({
                'name':item.prod.xProd
            })
        else:
            return False

    def checa_produtos(self):
        if not self.nfe_xml:
            raise UserError('Por favor, insira um arquivo de NFe.')
        nfe_string = base64.b64decode(self.nfe_xml)
        nfe = objectify.fromstring(nfe_string)
        items = []
        for det in nfe.NFe.infNFe.det:
            item = self.carrega_produtos(det, nfe)
            if item:
                items.append(item.id)
        if items:
            self.not_found_product = self.env['not.found.products'].browse(items)
        self.confirma = True
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.import.nfe',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

class NotFoundProduct(models.Model):
    _name = 'not.found.products'

    product_id = fields.Many2one('product.product', string="Produto no Sistema")
    name = fields.Char(string="Produto da NFe")
