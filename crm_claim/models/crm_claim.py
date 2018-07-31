# -*- coding: utf-8 -*-
# Copyright 2015-2017 Odoo S.A.
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import odoo
from odoo import _, api, fields, models
from odoo.tools import html2plaintext


class CrmClaim(models.Model):
    """ Crm claim"""

    _name = "crm.claim"
    _description = "Claim"
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    @api.model
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        team_id = self.env['crm.team']._get_default_team_id()
        return self.stage_find(team_id.id, [('sequence', '=', '1')])

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    name = fields.Char(
        string='Reclamação',
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
    action_next = fields.Char(
        string='Próxima Ação',
    )
    date_action_next = fields.Datetime(
        string='Data da Ação',
    )
    description = fields.Text(string=u'Descrição')
    resolution = fields.Text(string=u'Solução')
    create_date = fields.Datetime(
        string='Data de Criação',
        readonly=True,
    )
    write_date = fields.Datetime(
        string='Data de Atualização',
        readonly=True,
    )
    date_deadline = fields.Date(
        string='Final do Prazo',
    )
    date_closed = fields.Datetime(
        string='Data de Finalização',
        readonly=True,
    )
    date = fields.Datetime(
        string='Data da Reclamação',
        index=True,
        detault=fields.Datetime.now,
    )
    model_ref_id = fields.Reference(
        selection=odoo.addons.base.res.res_request.referenceable_models,
        string='Referência',
        oldname='ref',
    )
    categ_id = fields.Many2one(
        comodel_name='crm.claim.category',
        string='Categoria',
    )
    priority = fields.Selection(
        selection=[
            ('0', 'Baixa'),
            ('1', 'Normal'),
            ('2', 'Alta'),
        ],
        default='1',
    )
    type_action = fields.Selection(selection=[('correction', 'Ação Corretiva'),
                                              ('prevention', 'Ação Preventiva'), ], string='Tipo de Ação')
    user_id = fields.Many2one(comodel_name='res.users', string='Responsável Por Solucionar', track_visibility='always',
        default=lambda self: self.env.user)

    team_id = fields.Many2one(comodel_name='crm.team', string='Equipe de Vendas', index=True, default=_get_default_team,
        help="Equipe de Vendas Responsável.")

    company_id = fields.Many2one(comodel_name='res.company', string=u'Empresa',
                                 default=lambda self: self.env.user.company_id)

    partner_id = fields.Many2one(comodel_name='res.partner', string=u'Cliente')

    email_cc = fields.Text(string='Seguidores',
        help="Estes endereços de email seão adicionados ao campo CC em todos os emails.")

    email_from = fields.Char(string='Email', help="Email do destinatário.")

    partner_phone = fields.Char(string='Telefone')

    stage_id = fields.Many2one(comodel_name='crm.claim.stage', string='Estágio', track_visibility='onchange',
        default=_get_default_stage_id, domain="['|', ('team_ids', '=', team_id), ('case_default', '=', True)]")

    def stage_find(self, team_id, domain=None, order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - team_id: if set, stages must belong to this team or
              be a default case
        """
        if domain is None:  # pragma: no cover
            domain = []
        # collect all team_ids
        team_ids = []
        if team_id:
            team_ids.append(team_id)
        team_ids.extend(self.mapped('team_id').ids)
        search_domain = []
        if team_ids:
            search_domain += ['|'] * len(team_ids)
            for team_id in team_ids:
                search_domain.append(('team_ids', '=', team_id))
        search_domain.append(('case_default', '=', True))
        # AND with the domain in parameter
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['crm.claim.stage'].search(search_domain, order=order,
                                                  limit=1).id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """This function returns value of partner address based on partner
           :param email: ignored
        """
        if self.partner_id:
            self.email_from = self.partner_id.email
            self.partner_phone = self.partner_id.phone

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.stage_id:
            self.team_id = self.categ_id.team_id

    @api.model
    def create(self, values):
        ctx = self.env.context.copy()
        if values.get('team_id') and not ctx.get('default_team_id'):
            ctx['default_team_id'] = values.get('team_id')
        return super(CrmClaim, self.with_context(context=ctx)).create(values)

    @api.multi
    def copy(self, default=None):
        default = dict(
            default or {},
            stage_id=self._get_default_stage_id(),
            name=_('%s (copy)') % self.name,
        )
        return super(CrmClaim, self).copy(default)

    # -------------------------------------------------------
    # Mail gateway
    # -------------------------------------------------------
    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(CrmClaim, self).message_new(msg, custom_values=defaults)
