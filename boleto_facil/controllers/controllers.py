# -*- coding: utf-8 -*-
from odoo import http

# class BoletoFacil(http.Controller):
#     @http.route('/boleto_facil/boleto_facil/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/boleto_facil/boleto_facil/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('boleto_facil.listing', {
#             'root': '/boleto_facil/boleto_facil',
#             'objects': http.request.env['boleto_facil.boleto_facil'].search([]),
#         })

#     @http.route('/boleto_facil/boleto_facil/objects/<model("boleto_facil.boleto_facil"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('boleto_facil.object', {
#             'object': obj
#         })