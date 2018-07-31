# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):

    _inherit = "res.partner"

    birthday_date = fields.Date(string=u'Data de Aniversário')