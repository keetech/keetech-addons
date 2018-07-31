# -*- coding: utf-8 -*-
# Copyright 2015-2017 Odoo S.A.
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CrmClaimStage(models.Model):
    """ Model for claim stages. This models the main stages of a claim
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "crm.claim.stage"
    _description = "Estágios de Reclamações"
    _order = "sequence"

    name = fields.Char(string='Nome do Estágio', required=True, translate=True)

    sequence = fields.Integer(default=1, help="Use a sequência para ordernar os estágios.")

    team_ids = fields.Many2many(comodel_name='crm.team', relation='crm_team_claim_stage_rel', column1='stage_id',
                                column2='team_id', string='Teams',
                                help="Equipes de Vendas que podem usar o estágio da reclamação.")

    case_default = fields.Boolean(string='Definir Como Padrão',
                                  help="Se marcar este campo, este estágio será padrão nas reclamações.")
