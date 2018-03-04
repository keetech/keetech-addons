# -*- coding: utf-8 -*-
from odoo import http

# class PosBrNfce(http.Controller):
#     @http.route('/pos_br_nfce/pos_br_nfce/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_br_nfce/pos_br_nfce/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_br_nfce.listing', {
#             'root': '/pos_br_nfce/pos_br_nfce',
#             'objects': http.request.env['pos_br_nfce.pos_br_nfce'].search([]),
#         })

#     @http.route('/pos_br_nfce/pos_br_nfce/objects/<model("pos_br_nfce.pos_br_nfce"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_br_nfce.object', {
#             'object': obj
#         })