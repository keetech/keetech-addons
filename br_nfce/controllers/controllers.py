# -*- coding: utf-8 -*-
from odoo import http

# class BrNfce(http.Controller):
#     @http.route('/br_nfce/br_nfce/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/br_nfce/br_nfce/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('br_nfce.listing', {
#             'root': '/br_nfce/br_nfce',
#             'objects': http.request.env['br_nfce.br_nfce'].search([]),
#         })

#     @http.route('/br_nfce/br_nfce/objects/<model("br_nfce.br_nfce"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('br_nfce.object', {
#             'object': obj
#         })