from odoo import fields, models

class PaymentMode(models.Model):
    _inherit = "payment.mode"

    payment_method = fields.Selection([
        ('01', u'DINHEIRO'),
        ('02', u'CHEQUE'),
        ('03', u'BOLETO-FÁCIL'),
        ('04', u'BOLETO BANCÁRIO')
    ], string='Método do Pagamento')

    token = fields.Char(u'Token de Integração')
