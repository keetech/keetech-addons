# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Fillipe ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from datetime import timedelta


class Royalties(models.Model):
    _name = 'royalties'

    name = fields.Char()
    validity_date = fields.Date(string=u"Data de Término")
    start_date = fields.Date(string=u"Data Inicial")
    royalty_type = fields.Char(string=u"Referência")
    company_id = fields.Many2one("res.company", string=u"Company")
    payment_ids = fields.One2many("account.voucher", "royalties_id",
                                  readonly=True)
    line_ids = fields.One2many(
        'royalties.lines', 'royalties_id')
    partner_id = fields.Many2one('res.partner',
                                 string=u"Vendedor")
    #region = fields.Char(string=u"Região", size=20)
    state = fields.Selection(
        [('draft', u'Rascunho'), ('in_progress', u'Em Progresso'),
         ('waiting', u'Aguardando Pagamento'), ('done', u'Concluído')],
        default='draft',
        store=True,
        compute='_compute_state')
    actived = fields.Boolean(u"Ativo")
    done = fields.Boolean(u"Contrato Concluído")
    applied_on = fields.Selection([
        ('2_global', 'Todos os Produtos'),
        ('0_product', 'Produto'), ], "Aplicar em",
        default='2_global', required=True,
        help='Defina sobre quais itens o contrato de comissão será aplicado.')
    commission = fields.Float(string=u"% Comissão")
    min_qty = fields.Float(string=u"Qtd. mínima")

    def compute_commission(self):
        '''Função Utilizada para gerar as linhas de Fatura que serão
                usadas para calcular a comissão'''
        account_royalties_line = self.env['account.royalties.line']
        account_royalties_line.get_invoice_royaltie(self.id)
        self.royalties_payment()

    @api.one
    @api.constrains('validity_date', 'start_date')
    def _check_date(self):
        today = fields.date.today()
        start_date = fields.Date.from_string(self.start_date)
        validity_date = fields.Date.from_string(self.validity_date)
        if start_date < today:
            raise ValidationError(_(u"A data inicial do contrato não pode ser "
                                    "menor que a data de hoje!"))
        elif validity_date < today:
            raise ValidationError(_(u"A data final do contrato deve ser maior que "
                                    "a data inicial!"))
        elif validity_date > (today + timedelta(days=365)):
            raise ValidationError(_(u"O contrato não pode ter duração maior que "
                                    "1 ano, cheque as datas!"))

    @api.multi
    @api.depends('actived', 'done', 'validity_date', 'payment_ids')
    def _compute_state(self):
        inv_royalties_obj = self.env['account.royalties.line']
        for item in self:
            line_ids = inv_royalties_obj.search(
                [('voucher_id', '=', False),
                 ('royalties_id', '!=', False)])
            royalties_ids = line_ids.mapped('royalties_id')
            if item.actived and item.validity_date <= fields.Date.today():
                if royalties_ids and item.id in royalties_ids.ids:
                    item.state = 'waiting'
                else:
                    item.actived = False
                    item.done = True
                    item.state = 'done'
            elif item.actived:
                item.state = 'in_progress'
            elif item.done:
                item.state = 'done'
            elif not item.actived and not item.done:
                item.state = 'draft'

    @api.one
    def button_confirm(self):
        today = fields.date.today()
        if self.start_date < today:
            raise ValidationError(_(u"A data inicial do contrato não pode ser "
                                        "menor que a data de hoje!"))
        self.actived = True

    @api.multi
    def button_back_draft(self):
        for item in self:
            item.actived = False

    @api.multi
    def button_done(self):
        for item in self:
            item.actived = False
            item.done = True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('royalties')
        vals.update({'name': sequence})
        return super(Royalties, self).create(vals)

    @api.multi
    def royalties_payment(self):
        """
        Função que percorre as linhas de vendas comissionadas
        e gera um Voucher a pagar de comissão
        """
        inv_royalties_obj = self.env['account.royalties.line']
        voucher_obj = self.env['account.voucher']
        journal_id = self.env['account.journal'].search([
            ('special_royalties', '=', True)], limit=1)
        if not journal_id:
            raise Warning(_(u"Nenhum diário configurado para o pagamento de comissões!"))
        for item in self:
            voucher_id = voucher_obj.search([
                ('royalties_id', '=', item.id),
                ('state', '=', 'draft'),
                ('partner_id', '=', item.partner_id.id)], limit=1)

            if not voucher_id:
                values = {
                    'partner_id': item.partner_id.id,
                    'account_id':
                        item.partner_id.property_account_payable_id.id,
                    'date': fields.Date.today(),
                    'pay_now': 'pay_later',
                    'voucher_type': 'purchase',
                    'journal_id': journal_id.id,
                    'royalties_id': item.id,
                    'reference': u'Pagamento de Comissões(%s)' % item.name,
                }
                voucher_id = voucher_obj.create(values)

            # Incrmentar um switch na função
            if self.applied_on == '2_global':
                s_inv_roy_line = inv_royalties_obj.search(
                    [('royalties_id','=',self.id)],
                )
                product_ids = s_inv_roy_line.mapped('product_id')

            else:
                product_ids = item.line_ids.mapped('product_id')

            line_vals = []
            for prod_id in product_ids:
                royalties_line_ids = inv_royalties_obj.search(
                    [('voucher_id', '=', False),
                     ('royalties_id', '=', item.id),
                     ('product_id', '=', prod_id.id),
                     ('inv_line_id.invoice_id.date_invoice', '>=',
                      item.start_date)])

                royalties_line_total_ids = inv_royalties_obj.search(
                    [('royalties_id', '=', item.id),
                     ('product_id', '=', prod_id.id)])

                quantity_total_fee = 0

                for line in royalties_line_total_ids:
                    if line.is_devol:
                        quantity_total_fee -= line.inv_line_id.quantity
                    else:
                        quantity_total_fee += line.inv_line_id.quantity

                fee = item._get_royalties_fee(quantity_total_fee, prod_id)

                # Calcular Valor dos produtos e comissões
                amount = 0
                company_id = None
                for roy_line in royalties_line_ids:
                    if (roy_line.inv_line_id.invoice_id.state == 'paid' or
                            roy_line.inv_line_id.invoice_id.state == 'open'):

                        company_id = roy_line.inv_line_id.company_id.id
                        list_price = roy_line.inv_line_id.product_id.list_price
                        quantity = roy_line.inv_line_id.quantity
                        price_unit = roy_line.inv_line_id.price_unit
                        invoice_name = roy_line.inv_line_id.invoice_id.move_name
                        if roy_line.is_devol:
                            amount -= (price_unit * quantity)
                        else:
                            amount += (price_unit * quantity)

                if royalties_line_ids:
                    vals = {
                        'product_id': prod_id.id,
                        'quantity': 1,
                        'name': u'CONTRATO DE COMISSÃO - %s / FATURA - %s' %(item.name, invoice_name),
                        'price_unit': amount * fee,
                        'account_id': journal_id.default_debit_account_id.id,
                        'company_id': company_id,
                        'fee': fee
                    }
                    line_vals.append((0, 0, vals))
                    royalties_line_ids.write({'voucher_id': voucher_id.id})

            voucher_id.write({'line_ids': line_vals})

    def _get_royalties_fee(self, qty, product_id):
        self.ensure_one()
        result = False
        if self.applied_on == '0_product':
            for line in self.line_ids.sorted(key=lambda r: r.min_qty,
                                             reverse=True):
                if line.product_id.id == product_id.id and qty >= line.min_qty:
                    return line.commission / 100
        else:
            return self.commission / 100
        return result


class RoyaltiesLines(models.Model):
    _name = 'royalties.lines'

    product_id = fields.Many2one(
        'product.product', string=u"Product", required=False)
    commission = fields.Float(string=u"%Comissão")
    min_qty = fields.Float(string=u"Qtd. mínima", default=1)
    royalties_id = fields.Many2one('royalties', string=u"Contrato")
    applied_on = fields.Selection(related='royalties_id.applied_on')

    @api.one
    @api.constrains('commission')
    def _check_value(self):
        if self.commission < 0:
            raise ValidationError(
                _(u"The commission rate must be bigger than 0"))
        if self.commission > 100:
            raise ValidationError(
                _(u"The commission rate must be smaller than 100"))

    @api.one
    @api.constrains('commission')
    def _check_positive(self):
        if self.min_qty < 1:
            raise ValidationError(
                _(u"Quantity must be bigger than 1"))
