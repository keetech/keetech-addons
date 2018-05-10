# -*- coding: utf-8 -*-
from odoo import http

# class Salesman(http.Controller):
#     @http.route('/salesman/salesman/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/salesman/salesman/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('salesman.listing', {
#             'root': '/salesman/salesman',
#             'objects': http.request.env['salesman.salesman'].search([]),
#         })

#     @http.route('/salesman/salesman/objects/<model("salesman.salesman"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('salesman.object', {
#             'object': obj
#         })