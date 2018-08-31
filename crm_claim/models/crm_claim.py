# -*- coding: utf-8 -*-
# Copyright 2015-2017 Odoo S.A.
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import odoo
from odoo import _, api, fields, models
from odoo.tools import html2plaintext
from datetime import datetime
from odoo.exceptions import UserError

class CrmClaim(models.Model):
    """ Crm claim"""

    _name = "crm.claim"
    _description = "Claim"
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    name = fields.Char(string='Reclamação', required=True)
    active = fields.Boolean(default=True)
    action_next = fields.Char(string='Próxima Ação')
    date_action_next = fields.Datetime(string='Data da Ação')
    description = fields.Text(string=u'Descrição')
    resolution = fields.Text(string=u'Solução')
    create_date = fields.Datetime(string='Data de Criação', readonly=True)
    write_date = fields.Datetime(string='Data de Atualização', readonly=True)
    date_deadline = fields.Date(string='Final do Prazo', required=True)
    date_closed = fields.Datetime(string='Data de Finalização', readonly=True)
    date = fields.Datetime(string='Data da Reclamação', required=True, index=True, detault=fields.Datetime.now)
    model_ref_id = fields.Reference(selection=odoo.addons.base.res.res_request.referenceable_models,
                                    string='Referência', oldname='ref')
    categ_id = fields.Many2one(comodel_name='crm.claim.category', string='Categoria')
    priority = fields.Selection(selection=[('0', 'Baixa'), ('1', 'Normal'), ('2', 'Alta')], default='1')
    type_action = fields.Selection(selection=[('correction', 'Ação Corretiva'), ('prevention', 'Ação Preventiva'), ],
                                   string='Tipo de Ação')
    user_id = fields.Many2one(comodel_name='res.users', string='Responsável Por Solucionar', track_visibility='always',
        default=lambda self: self.env.user)
    team_id = fields.Many2one(comodel_name='crm.team', string='Equipe de Vendas', index=True, default=_get_default_team,
        help="Equipe de Vendas Responsável.")
    company_id = fields.Many2one(comodel_name='res.company', string=u'Empresa',
                                 default=lambda self: self.env.user.company_id)
    partner_id = fields.Many2one(comodel_name='res.partner', string=u'Cliente', required=True)
    claimant = fields.Char(string=u'Reportada Por', required=True)
    solve_partner = fields.Char(string=u'Resp Por Solucionar')
    email_cc = fields.Text(string='Seguidores',
                           help="Estes endereços de email seão adicionados ao campo CC em todos os emails.")
    email_from = fields.Char(string='Email', help="Email do destinatário.")
    partner_phone = fields.Char(string='Telefone')
    stage_id = fields.Selection([('open', 'Nova'), ('solved', 'Solucionada'), ('rejected', 'Rejeitada')],
                                string='Estágio', track_visibility='onchange', default='open')
    problem_origin = fields.Char(string=u'Origem do Problema')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        This function returns value of partner address based on partner
        :param email: ignored
        """
        if self.partner_id:
            self.email_from = self.partner_id.email
            self.partner_phone = self.partner_id.phone

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
            #stage_id=self._get_default_stage_id(),
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

    @api.multi
    def solve_claim(self):
        for claim in self:
            if claim.resolution == False:
                raise UserError(
                    _("Para marcar uma reclamação como solucionada por favor descreva a solução do problema."))
            elif len(claim.resolution) == 0:
                raise UserError(
                    _("Para marcar uma reclamação como solucionada por favor descreva a solução do problema."))
            claim.date_closed = datetime.now()
            claim.stage_id = 'solved'

    @api.multi
    def rejected_cleim(self):
        for claim in self:
            claim.date_closed = datetime.now()
            claim.stage_id = 'rejected'

