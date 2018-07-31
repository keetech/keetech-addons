# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api, _
import datetime, calendar
from odoo.exceptions import UserError, AccessError

class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    portfolio_salesman = fields.Many2many('salesman.partner', 'wallets')

class SalesmanPartner(models.Model):
    _name = 'salesman.partner'
    inherits = {'res.users': 'user_id'}

    partner_id = fields.Many2one('res.partner', related='user_id.partner_id', string="Parceiro",ondelete='restrict')
    user_id = fields.Many2one('res.users', string="Vendedor",required=True, ondelete='restrict', auto_join=True)
    name = fields.Char(related='user_id.partner_id.name')
    email = fields.Char(related='user_id.email', readonly=True)
    currency_id = fields.Many2one("res.currency", related='user_id.company_id.currency_id', string="Currency",
                                  readonly=True, required=True)
    count_sales = fields.Integer(string="Número de Vendas", compute='_compute_sales', readonly=True)
    amount_sales = fields.Monetary(string="Total de Vendas", compute='_compute_sales', readonly=True)
    count_sales_month = fields.Integer(string="Número de Vendas do Mês", compute='_compute_sales', readonly=True)
    amount_sales_month = fields.Float(string="Total de Vendasdo Mês", digits=(7, 2), compute='_compute_sales',
                                      readonly=True)
    portfolio_customer = fields.Many2many('res.partner', 'wallets', string='Carteira de Clientes')
    sales_goal = fields.Float(string="Meta do Vendedor", digits=(7, 2))
    sales_goal_reached = fields.Float(string="Percentual da Meta do Mês", digits=(3, 2), compute="_compute_goal")
    discountlimits_line = fields.One2many('salesman.discount.limits', 'salesman_id', string='Alçada de Descontos')

    @api.depends('sales_goal', 'amount_sales_month')
    def _compute_goal(self):
        for record in self:
            if record.amount_sales_month > 0 and record.sales_goal > 0:
                record.sales_goal_reached = (record.amount_sales_month / record.sales_goal) * 100

    @api.model
    def _compute_sales(self):
        sales = self.env['sale.order']
        today = datetime.datetime.today()
        month_start = datetime.datetime(today.year, today.month, 1)
        month_end = month_start + datetime.timedelta(days=calendar.monthrange(month_start.year,month_start.month)[1])
        month_start = datetime.datetime.strftime(month_start, "%Y-%m-%d %H:%M:%S")
        month_end = datetime.datetime.strftime(month_end, "%Y-%m-%d %H:%M:%S")
        for record in self:
            record.amount_sales_month = 0
            record.amount_sales = 0
            sales_of_user = sales.search([('user_id', '=', record.user_id.id), ('state', '=', 'sale')])
            record.count_sales = len(sales_of_user)
            if sales_of_user:
                for sale in sales_of_user:
                    record.amount_sales += sale.amount_total

            sales_of_user_month = sales.search([('user_id', '=', record.user_id.id), ('state', '=', 'sale'),
                ('confirmation_date', '>=', month_start),('confirmation_date', '<', month_end)])
            record.count_sales_month = len(sales_of_user_month)
            if sales_of_user_month:
                for sale in sales_of_user_month:
                    record.amount_sales_month += sale.amount_total

class SalesmanDiscountLimits(models.Model):
    _name = 'salesman.discount.limits'

    salesman_id = fields.Many2one('salesman.partner', string='Vendedor', required=True, ondelete='cascade', index=True,
                                  copy=False)
    product_id = fields.Many2one('product.product', string='Produto')
    category_id = fields.Many2one('product.category', string='Categoria')
    limit_discount = fields.Float(string='Limite de Desconto Concedido', digits=(3, 2))


class SalesDiscount(models.TransientModel):
    _name = 'discount.approve'

    user_id = fields.Many2one('res.users', string='Aprovador', track_visibility='onchange',
                    default=lambda self: self.env.user)
    discounts_line = fields.Many2many('discounts.approve.lines', string='Descontos Pendentes')

    @api.multi
    @api.onchange('user_id')
    def compute_discount_lines(self):
        order_lines = self.env['sale.order.line']
        discounts_waiting_approve = order_lines.search([('discount_status', '=', 'waiting')])
        if discounts_waiting_approve:
            lines_to_approve = self.env['discounts.approve.lines']
            lines = []
            for line in discounts_waiting_approve:
                item = lines_to_approve.create({'sale_order_line': line.id})
                lines.append(item.id)

            self.discounts_line = lines_to_approve.browse(lines)

class SalesDiscount(models.TransientModel):
    _name = 'discounts.approve.lines'

    sale_order_line = fields.Many2one('sale.order.line')
    product_id = fields.Many2one('product.product', related='sale_order_line.product_id', string='Produto',
                                 readonly=True)
    salesman = fields.Many2one('res.users',related='sale_order_line.order_id.user_id', string='Vendedor', readonly=True)
    price_unit = fields.Float(related='sale_order_line.price_unit', string='Vlr. Unit.', readonly=True)
    product_uom_qty = fields.Float(related='sale_order_line.product_uom_qty', string='Qtd.', readonly=True)
    product_uom = fields.Many2one('product.uom', string='Unidade de Medida', related='sale_order_line.product_uom')
    discount = fields.Float(string='%Desc', related='sale_order_line.discount', readonly=True)
    amount_discount = fields.Float(string='Vlr Desc', compute='_compute_amount')
    amount_without_discount = fields.Float(string='Total S/ Desc', compute='_compute_amount')
    amount_total = fields.Float(string='Total C/ Desc', compute='_compute_amount')
    allow = fields.Boolean(string='Aprovar', store=True)
    refuse = fields.Boolean(string='Negar', store=True)

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'discount.approve',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    @api.depends('sale_order_line', 'product_uom_qty', 'price_unit', 'discount')
    def _compute_amount(self):
        for record in self:
            record.amount_without_discount = record.price_unit * record.product_uom_qty
            record.amount_discount = (record.discount / 100) * record.amount_without_discount
            record.amount_total = record.amount_without_discount - record.amount_discount

    @api.multi
    def approve_discount(self):
        self.sale_order_line.discount_status = 'approve'
        self.sale_order_line.discount_approver = self.env.user

        return self._reopen_form()

    @api.multi
    def refuse_discount(self):
        self.sale_order_line.discount_status = 'refuse'
        self.sale_order_line.discount_approver = self.env.user

        return self._reopen_form()

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    limit_discount = fields.Float(string='Desconto Pemitido', compute='_compute_discount',digits=(3, 2))
    discount_status = fields.Selection([('approve','Aprovar'),('refuse','Recusar'),('waiting','Aguardando Aprovação'),
                                        ('allowed', 'Permitido')],store=True)
    discount_approver = fields.Many2one('res.users', string='Aprovador do Desconto')

    @api.one
    @api.depends('product_id.product_tmpl_id.categ_id')
    def discover_category_parents(self):
        list_category = []
        category = self.product_id.product_tmpl_id.categ_id
        while category.parent_id:
            list_category.append(category.parent_id.id)
            category = category.parent_id

        return list_category

    @api.one
    @api.depends('product_id', 'order_id.user_id', 'product_id.product_tmpl_id.categ_id', 'state')
    def _compute_discount(self):
        salesman = self.env['salesman.partner'].search([('user_id', '=', self.order_id.user_id.id)])
        limit_discount = 0
        if len(salesman) == 1:
            category = self.product_id.product_tmpl_id.categ_id
            if len(category) > 0:
                category_discount = self.env['salesman.discount.limits'].search([('salesman_id', '=', salesman.id),\
                    ('category_id', '=', category.id)])
                list_categorys = self.discover_category_parents()
                if category_discount:
                    limit_discount = category_discount.limit_discount
                if not category_discount and list_categorys:
                    for parent in list_categorys:
                        category_discount = self.env['salesman.discount.limits'].search\
                            ([('salesman_id', '=', salesman.id), ('category_id', '=', parent)])
                        limit_discount = category_discount.limit_discount

            product = self.product_id
            if len(product) == 1:
                product_discount = self.env['salesman.discount.limits'].search([('salesman_id', '=', salesman.id),\
                    ('product_id', '=', product.id)])
                if product_discount:
                    limit_discount = product_discount.limit_discount

        self.limit_discount = limit_discount

        for record in self:
            if record.discount_status not in ['allowed', 'refuse', 'approve']:
                if record.discount > 0 and record.state == 'draft':
                    if record.discount > limit_discount:
                        record.discount_status = 'waiting'
                    if record.discount < limit_discount:
                        record.discount_status = 'allowed'

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def validation_discount(self):
        disc_message = []
        message = ''
        for item in self.order_line:
            if item.discount_status == 'waiting':
                message += "(%s) com desconto acima do permitido solicite aprovação do gerente"% (item.product_id.name)
                message += " ou reduza o desconto para seu limite permitido.\n"
            if item.discount_status == 'refuse':
                message += "(%s) com desconto não aprovado pelo gerente,"% (item.product_id.name)
                message += " reduza o desconto para seu limite permitido.\n"

        if len(message) > 0:
            disc_message.append(message)

        return disc_message

    @api.multi
    def action_confirm(self):
        disc_message = self.validation_discount()
        if len(disc_message) > 0:
            raise UserError(disc_message)

        return super(SaleOrder, self).action_confirm()

