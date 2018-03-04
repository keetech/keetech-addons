# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_template(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):

        # Get Next code from category
        if vals.get('categ_id', False) != False and vals.get('default_code', False) == False:
            category = self.env['product.category'].browse(vals['categ_id'])
            if vals.get('default_code', False) == False:
                vals['default_code'] = category.get_next_id()

        return super(product_template, self).create(vals)
