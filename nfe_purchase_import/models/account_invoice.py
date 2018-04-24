# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, datetime
import base64
from lxml import objectify

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    nfe_num = fields.Integer('Num. NFe')
    nfe_serie = fields.Char('Série')
    nfe_modelo = fields.Char('Modelo')
    nfe_chave =  fields.Char('Chave NFe')
    nfe_emissao = fields.Date('Data Emissão NFe')
    xml_purchase = fields.Binary(string=u"Xml da NFe", readonly=True)

    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self).create(vals)
        purchase = invoice.invoice_line_ids.mapped('purchase_line_id.order_id')
        if purchase and not invoice.refund_invoice_id:
            if purchase:
                invoice.nfe_num = purchase.nfe_num
                invoice.nfe_serie = purchase.nfe_serie
                invoice.nfe_modelo = purchase.nfe_modelo
                invoice.nfe_chave = purchase.nfe_chave
                invoice.nfe_emissao = purchase.nfe_emissao
                invoice.xml_purchase = purchase.xml_purchase
            message = _("This vendor bill has been created from: %s") % \
                      (",".join(["<a href=# data-oe-model=purchase.order data-oe-id="\
                                 +str(order.id)+">"+order.name+"</a>" for order in purchase]))
            invoice.message_post(body=message)
        return invoice
    '''
    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line)

        #if line.xml_purchase:
        #    res['qty'] = line.product_qty - line.qty_invoiced
        return res
    '''

    @api.multi
    def action_move_create(self):
        """
        Substitui a função original parar criar os movimentos financeiros.
        Inclui regra para verificar se existem pagamentos relacionados no XML
        e cria os vencimentos conforme o XML
        Creates invoice related analytics and financial move lines
        """
        account_move = self.env['account.move']
        #import pudb; pu.db
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.with_context(ctx).write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get() #cria os vencimentos sem impostos
            iml += inv.tax_line_move_line_get() #cria os vencimentos de impostos

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.type == 'in_invoice':
                nfe_string = base64.b64decode(inv.xml_purchase)
                nfe = objectify.fromstring(nfe_string)
            # Se a fatura for criada através de XML importado irá percorrer as cobranças do XML
            if inv.type == 'in_invoice' and inv.nfe_num != False and hasattr(nfe.NFe.infNFe, 'cobr'):
                num_nfe = nfe.NFe.infNFe.ide.nNF
                vencimentos = nfe.NFe.infNFe.cobr.dup
                res_amount_currency = total_currency
                ctx['date'] = inv._get_currency_rate_date()
                i = 0

                for dup in vencimentos:
                    i += 1
                    valor = float(dup.vDup)
                    valor = company_currency.round(valor)
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(valor, inv.currency_id)
                    else:
                        amount_currency = False

                    res_amount_currency -= amount_currency or 0

                    #if i == len(totlines):
                    #    amount_currency += res_amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': -(valor),
                        'account_id': inv.account_id.id,
                        'date_maturity': dup.dVenc,
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })


            elif inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv._get_currency_rate_date()
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)

        return True