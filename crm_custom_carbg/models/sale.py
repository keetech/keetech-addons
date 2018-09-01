from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_products_id = fields.One2many('product.product', compute='compute_partner_products')

    @api.onchange('partner_id')
    def compute_partner_products(self):
        products = []
        product_product = self.env['product.product']
        for record in self:
            if record.partner_id.property_product_pricelist.item_ids:
                for product in record.partner_id.property_product_pricelist.item_ids:
                    products.append(product.product_tmpl_id.id)
            product_product = product_product.search([('product_tmpl_id', 'in', products)])
            product_list = []
            for p in product_product:
                product_list.append(p.id)

            record.partner_products_id = [(6, 0, product_list)]