# -*- coding: utf-8 -*-
from odoo import http

# class BrNfeExtend(http.Controller):
#     @http.route('/br_nfe_extend/br_nfe_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/br_nfe_extend/br_nfe_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('br_nfe_extend.listing', {
#             'root': '/br_nfe_extend/br_nfe_extend',
#             'objects': http.request.env['br_nfe_extend.br_nfe_extend'].search([]),
#         })

#     @http.route('/br_nfe_extend/br_nfe_extend/objects/<model("br_nfe_extend.br_nfe_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('br_nfe_extend.object', {
#             'object': obj
#         })