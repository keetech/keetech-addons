# -*- coding: utf-8 -*-
from odoo import http

# class KSaleCustomDateOrder(http.Controller):
#     @http.route('/k_sale_custom_date_order/k_sale_custom_date_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/k_sale_custom_date_order/k_sale_custom_date_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('k_sale_custom_date_order.listing', {
#             'root': '/k_sale_custom_date_order/k_sale_custom_date_order',
#             'objects': http.request.env['k_sale_custom_date_order.k_sale_custom_date_order'].search([]),
#         })

#     @http.route('/k_sale_custom_date_order/k_sale_custom_date_order/objects/<model("k_sale_custom_date_order.k_sale_custom_date_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('k_sale_custom_date_order.object', {
#             'object': obj
#         })