# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmTechicalCalled(models.Model):

    _name = "crm.technical.called"

    name = fields.Char(u'Título', compute='_compute_name')
    date = fields.Date(u'Data do Chamado', readonly=True, required=True,
                       states={'open': [('readonly', False)], 'late': [('readonly', False)]})
    deadline = fields.Date(u'Data do Atendimento', readonly=True, required=True,
                           states={'open': [('readonly', False)], 'late': [('readonly', False)]})
    responsible = fields.Char(u'Atendente', readonly=True, required=True,
                              states={'open': [('readonly', False)], 'late': [('readonly', False)]})
    description = fields.Char(u'Descrição do Suporte', readonly=True,
                              states={'open': [('readonly', False)], 'late': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string=u'Cliente', required=True, readonly=True,
                                 states={'open': [('readonly', False)]})
    state = fields.Selection([('open', u'Aberto'), ('done', u'Concluído'), ('late', u'Atrasado'),
                              ('missing', u'Não Atendido')], string=u'Estado', default='open')

    @api.multi
    def done_called(self):
        for record in self:
            if record.state in ['open', 'late']:
                record.state = 'done'
                return
            else:
                return

    @api.multi
    def missing_called(self):
        for record in self:
            if record.state in ['open', 'late']:
                record.state = 'missing'
                return
            else:
                return

    def _compute_name(self):
        for record in self:
            label = u'[%s] Chamado Técnico - ' % (record.id)
            record.name = label + record.partner_id.name

class CrmSuggestions(models.Model):

    _name = "crm.suggestions"

    name = fields.Char(compute='_compute_name')
    partner_id = fields.Many2one('res.partner', string=u'Cliente', required=True)
    reporter = fields.Char(string=u'Reportado por', required=True)
    date = fields.Date(string=u'Data', required=True)
    suggestion = fields.Selection([('suggestion', u'Sugestão'), ('compliment', u'Elogio')],
                                  string=u'Sugestão/Elogio', required=True)
    description = fields.Char(string=u'Descrição', required=True)

    def _compute_name(self):
        for record in self:
            if record.suggestion == 'suggestion':
                label = u'[%s] Sugestão - ' % record.id
                record.name = label + record.partner_id.name
            elif record.suggestion == 'compliment':
                label = u'[%s] Elogio - ' % record.id
                record.name = label + record.partner_id.name

