# -*- coding: utf-8 -*-
# Copyright 2015-2017 Odoo S.A.
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CrmClaimCategory(models.Model):
    _name = "crm.claim.category"
    _description = "Categoria de Reclamações"

    name = fields.Char(string='Nome da Categoria', required=True, translate=True)
    team_id = fields.Many2one(comodel_name='crm.team', string='Equipe de Vendas')
