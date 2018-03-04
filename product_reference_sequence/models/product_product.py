# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_product(models.Model):
    _inherit = "product.product"

        
    @api.model
    def create(self, vals):

        # Get original code from template
        if vals.get('product_tmpl_id', False) != False and vals.get('default_code', False) == False:
            template = self.env['product.template'].browse(vals['product_tmpl_id'])
            if template.default_code:
                vals['default_code'] = template.default_code
            elif template.categ_id:
                vals['default_code'] = template.categ_id.get_next_id()
            
        # Get Next code from category
        if vals.get('categ_id', False) != False and vals.get('default_code', False) == False:
            category = self.env['product.category'].browse(vals['categ_id'])
            if vals.get('default_code', False) == False:
                vals['default_code'] = category.get_next_id()

        return super(product_product, self).create(vals)
