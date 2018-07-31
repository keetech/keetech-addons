# -*- coding: utf-8 -*-
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models,SUPERUSER_ID
from odoo import tools

import math
import datetime
import logging
from random import randint
from dateutil import tz

_logger = logging.getLogger(__name__)

class WebsiteSupportTicket(models.Model):

    _name = "website.support.ticket"
    _description = "Website Support Ticket"
    _rec_name = "subject"
    _inherit = ['mail.thread']

    @api.model
    def _read_group_state(self, states, domain, order):
        """ Read group customization in order to display all the states in the
            kanban view, even if they are empty
        """
        
        staff_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_replied')
        customer_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')
        customer_closed = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_closed')
        staff_closed = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_closed')
        
        exclude_states = [staff_replied_state.id, customer_replied_state.id, customer_closed.id, staff_closed.id]
        
        #state_ids = states._search([('id','not in',exclude_states)], order=order, access_rights_uid=SUPERUSER_ID)
        state_ids = states._search([], order=order, access_rights_uid=SUPERUSER_ID)
        
        return states.browse(state_ids)

    def _default_state(self):
        return self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')

    def _default_priority_id(self):
        default_priority = self.env['website.support.ticket.priority'].search([('sequence','=','1')])
        return default_priority[0]

    def _default_approval_id(self):
        return self.env['ir.model.data'].get_object('website_support', 'no_approval_required')

    name = fields.Char(string=u'Ticket', compute='compute_ticket_name')
    channel = fields.Char(string="Channel", default="Manual", readonly=True)
    create_user_id = fields.Many2one('res.users', "Create User")
    priority_id = fields.Many2one('website.support.ticket.priority', default=_default_priority_id, string="Priority")
    partner_id = fields.Many2one('res.partner', string='Cliente')
    user_id = fields.Many2one('res.users', string='Responsável Pelo Atendimento')
    person_name = fields.Char(string='Solicitante')
    email = fields.Char(string="Email")
    email_cc = fields.Char(string='Watchers Emails')
    support_email = fields.Char(string="Support Email")
    category = fields.Many2one('website.support.ticket.categories', string="Categoria", track_visibility='onchange')
    sub_category_id = fields.Many2one('website.support.ticket.subcategory', string="Sub-Categoria")
    subject = fields.Char(string=u'Resumo', required=True)
    description = fields.Text(string=u'Descrição do Problema/Suporte')
    state = fields.Many2one('website.support.ticket.states', group_expand='_read_group_state', default=_default_state, string="State")
    conversation_history = fields.One2many('website.support.ticket.message', 'ticket_id', string=u'Histórico de Mensagens')
    attachment = fields.Binary(string=u'Anexo')
    attachment_filename = fields.Char(string=u'Nome do Anexo')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'website.support.ticket')], string=u'Anexos')
    unattended = fields.Boolean(string="Unattended", compute="_compute_unattend", store="True", help="In 'Open' state or 'Customer Replied' state taken into consideration name changes")
    portal_access_key = fields.Char(string="Portal Access Key")
    ticket_number = fields.Integer(string="Número do Ticket")
    ticket_number_display = fields.Char(string="Número do Ticket", compute="_compute_ticket_number_display")
    ticket_color = fields.Char(related="priority_id.color", string="Cor do Ticket")
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env['res.company']._company_default_get('website.support.ticket') )
    support_rating = fields.Integer(string="Avaliação do Atendimento")
    support_comment = fields.Text(string="Support Comment")
    close_comment = fields.Text(string="Close Comment")
    close_time = fields.Datetime(string="Close Time")
    close_date = fields.Date(string="Close Date")
    closed_by_id = fields.Many2one('res.users', string="Finalizado Por")
    time_to_close = fields.Integer(string="Time to close (seconds)")
    extra_field_ids = fields.One2many('website.support.ticket.field', 'wst_id', string="Extra Details")
    planned_time = fields.Datetime(string="Planned Time")
    planned_time_format = fields.Char(string="Planned Time Format", compute="_compute_planned_time_format")
    approval_id = fields.Many2one('website.support.ticket.approval', default=_default_approval_id, string="Approval")
    approval_message = fields.Text(string="Approval Message")
    approve_url = fields.Char(compute="_compute_approve_url", string="Approve URL")
    disapprove_url = fields.Char(compute="_compute_disapprove_url", string="Disapprove URL")
    tag_ids = fields.Many2many('website.support.ticket.tag', string="Tags")
    sla_id = fields.Many2one('website.support.sla', string="SLA")
    sla_timer = fields.Float(string="SLA Time Remaining")
    sla_timer_format = fields.Char(string="SLA Timer Format", compute="_compute_sla_timer_format")
    sla_active = fields.Boolean(string="SLA Active")
    sla_response_category_id = fields.Many2one('website.support.sla.response', string="SLA Response Category")
    sla_alert_ids = fields.Many2many('website.support.sla.alert', string="SLA Alerts", help="Keep record of SLA alerts sent so we do not resend them")

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        create_context = dict(self.env.context or {})
        create_context['default_user_id'] = False
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'person_name': msg.get('author_id'),
            'partner_id': msg.get('author_id'),
            'email': msg.get('from'),
            'channel': 'Email',
            'email_cc': msg.get('cc'),
        }
        defaults.update(custom_values)

        ticket = super(WebsiteSupportTicket, self.with_context(create_context)).message_new(msg, custom_values=defaults)
        email_list = task.email_split(msg)
        partner_ids = [p for p in ticket._find_partner_from_emails(email_list, force_create=False) if p]
        ticket.message_subscribe(partner_ids)
        return ticket

    @api.multi
    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        aliases = self.mapped('category.alias_name')
        return [x for x in email_list if x.split('@')[0] not in aliases]

    @api.multi
    @api.depends('ticket_number')
    def compute_ticket_name(self):
        for record in self:
            if ticket_number != False:
                record.name = 'Ticket [%s]' + ticket_number
            else:
                record.name = 'Rascunho'

    @api.one
    @api.depends('sla_timer')
    def _compute_sla_timer_format(self):
        #Exibe horas negativas em formato positivo
        self.sla_timer_format = '{0:02.0f}:{1:02.0f}'.format(*divmod(abs(self.sla_timer) * 60, 60))

    @api.model
    def update_sla_timer(self):
        
        #Subtract 1 minute from the timer of all active SLA tickets, this includes going into negative
        for active_sla_ticket in self.env['website.support.ticket'].search([('sla_active','=',True), ('sla_id','!=',False), ('sla_response_category_id','!=',False)]):

            #If we only countdown during busines hours
            if active_sla_ticket.sla_response_category_id.countdown_condition == 'business_only':
                #Check if the current time aligns with a timeslot in the settings, setting has to be set for business_only or UserError occurs
                setting_business_hours_id = self.env['ir.default'].get('website.support.settings', 'business_hours_id')
                current_hour = datetime.datetime.now().hour
                current_minute = datetime.datetime.now().minute / 60
                current_hour_float = current_hour + current_minute
                day_of_week = datetime.datetime.now().weekday()
                during_work_hours = self.env['resource.calendar.attendance'].search([('calendar_id','=', setting_business_hours_id), ('dayofweek','=',day_of_week), ('hour_from','<',current_hour_float), ('hour_to','>',current_hour_float)])

                #If holiday module is installed take into consideration
                holiday_module = self.env['ir.module.module'].search([('name','=','hr_public_holidays'), ('state','=','installed')])
                if holiday_module:
                    holiday_today = self.env['hr.holidays.public.line'].search([('date','=',datetime.datetime.now().date())])
                    if holiday_today:
                        during_work_hours = False

                if during_work_hours:
                    active_sla_ticket.sla_timer -= 1/60
            else:
                #Countdown even if the business hours setting is not set
                active_sla_ticket.sla_timer -= 1/60

            #Send an email out to everyone in the category about the SLA alert
            notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_sla_alert')

            for sla_alert in self.env['website.support.sla.alert'].search([('vsa_id','=',active_sla_ticket.sla_id.id), ('alert_time','>=', active_sla_ticket.sla_timer)]):

                #Only send out the alert once
                if sla_alert not in active_sla_ticket.sla_alert_ids:

                    for my_user in active_sla_ticket.category.cat_user_ids:
                        values = notification_template.generate_email(active_sla_ticket.id)
                        values['body_html'] = values['body_html'].replace("_user_name_",  my_user.partner_id.name)
                        values['email_to'] = my_user.partner_id.email

                        send_mail = self.env['mail.mail'].create(values)
                        send_mail.send()

                        #Remove the message from the chatter since this would bloat the communication history by a lot
                        send_mail.mail_message_id.res_id = 0

                    #Add the alert to the list of already sent SLA
                    active_sla_ticket.sla_alert_ids = [(4, sla_alert.id)]

    def pause_sla(self):
        self.sla_active = False

    def resume_sla(self):
        self.sla_active = True

    @api.one
    @api.depends('planned_time')
    def _compute_planned_time_format(self):
    
        #If it is assigned to the partner, use the partners timezone and date formatting
        if self.planned_time and self.partner_id and self.partner_id.lang:
            partner_language = self.env['res.lang'].search([('code','=', self.partner_id.lang)])[0]
            
            my_planned_time = datetime.datetime.strptime(self.planned_time, DEFAULT_SERVER_DATETIME_FORMAT)

            #If we have timezone information translate the planned date to local time otherwise UTC
            if self.partner_id.tz:
                my_planned_time = my_planned_time.replace(tzinfo=tz.gettz('UTC'))
                local_time = my_planned_time.astimezone(tz.gettz(self.partner_id.tz))
                self.planned_time_format = local_time.strftime(partner_language.date_format + " " + partner_language.time_format) + " " + self.partner_id.tz
            else:
                self.planned_time_format = my_planned_time.strftime(partner_language.date_format + " " + partner_language.time_format) + " UTC"
            
        else:
            self.planned_time_format = self.planned_time
        
    @api.one
    def _compute_approve_url(self):
        self.approve_url = "/support/approve/" + str(self.id)

    @api.one
    def _compute_disapprove_url(self):
        self.disapprove_url = "/support/disapprove/" + str(self.id)

    @api.onchange('sub_category_id')
    def _onchange_sub_category_id(self):
        if self.sub_category_id:
            
            add_extra_fields = []
            
            for extra_field in self.sub_category_id.additional_field_ids:
                add_extra_fields.append((0, 0, {'name': extra_field.name}))
                
            self.update({
                'extra_field_ids': add_extra_fields,
            })

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.person_name = self.partner_id.name
        self.email = self.partner_id.email

    def message_new(self, msg, custom_values=None):
        """Cria novo ticket de suporte ao receber novo email"""

        defaults = {'support_email': msg.get('to'), 'subject': msg.get('subject')}

        #Extrair o nome do email
        if "<" in msg.get('from') and ">" in msg.get('from'):
            start = msg.get('from').rindex( "<" ) + 1
            end = msg.get('from').rindex( ">", start )
            from_email = msg.get('from')[start:end]
            from_name = msg.get('from').split("<")[0].strip()
            defaults['person_name'] = from_name
        else:
            from_email = msg.get('from')

        defaults['email'] = from_email
        defaults['channel'] = "Email"

        #Tenta localizar o parceiro através do remetente do email
        search_partner = self.env['res.partner'].sudo().search([('email','=', from_email)])
        if len(search_partner) > 0:
            defaults['partner_id'] = search_partner[0].id
            defaults['person_name'] = search_partner[0].name

        defaults['description'] = tools.html_sanitize(msg.get('body'))

        #Atribui a categoria padrão
        setting_email_default_category_id = self.env['ir.default'].get('website.support.settings', 'email_default_category_id')

        if setting_email_default_category_id:
            defaults['category'] = setting_email_default_category_id

        return super(WebsiteSupportTicket, self).message_new(msg, custom_values=defaults)

    def message_update(self, msg_dict, update_vals=None):
        """ Substituir para atualizar o ticket de suporte de acordo com o email. """

        body_short = tools.html_sanitize(msg_dict['body'])
        #body_short = tools.html_email_clean(msg_dict['body'], shorten=True, remove=True)

        #Add to message history to keep HTML clean
        self.conversation_history.create({'ticket_id': self.id, 'by': 'customer', 'content': body_short })

        #If the to email address is to the customer then it must be a staff member
        if msg_dict.get('to') == self.email:
            change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')
        else:
            change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_customer_replied')

        self.state = change_state.id

        return super(WebsiteSupportTicket, self).message_update(msg_dict, update_vals=update_vals)

    @api.one
    @api.depends('ticket_number')
    def _compute_ticket_number_display(self):
        if self.ticket_number:
            self.ticket_number_display = "#" + "{:,}".format(self.ticket_number).replace(',', '.')

    @api.one
    @api.depends('state')
    def _compute_unattend(self):
        opened_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        customer_replied_state = self.env['ir.model.data'].get_object('website_support',
                                                                      'website_ticket_state_customer_replied')

        if self.state == opened_state or self.state == customer_replied_state:
            self.unattended = True

    @api.multi
    def request_approval(self):

        approval_email = self.env['ir.model.data'].get_object('website_support', 'support_ticket_approval')

        values = self.env['mail.compose.message'].generate_email_for_composer(approval_email.id, [self.id])[self.id]

        request_message = values['body']

        return {
            'name': "Request Approval",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.compose',
            'context': {'default_ticket_id': self.id, 'default_email': self.email, 'default_subject': self.subject, 'default_approval': True, 'default_body': request_message},
            'target': 'new'
        }
        
    @api.multi
    def open_close_ticket_wizard(self):

        return {
            'name': "Close Support Ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.close',
            'context': {'default_ticket_id': self.id},
            'target': 'new'
        }

    @api.model
    def _needaction_domain_get(self):
        open_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        custom_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')
        return ['|',('state', '=', open_state.id ), ('state', '=', custom_replied_state.id)]

    @api.model
    def create(self, vals):
        new_id = super(WebsiteSupportTicket, self).create(vals)

        new_id.portal_access_key = randint(1000000000,2000000000)
        
        new_id.ticket_number = new_id.company_id.next_support_ticket_number

        #Adiciona o próximo número de ticket
        new_id.company_id.next_support_ticket_number += 1

        ticket_open_email_template = self.env['ir.model.data'].get_object('website_support',
                                                                          'website_ticket_state_open').mail_template_id
        ticket_open_email_template.send_mail(new_id.id, True)

        #Verifica se o contato possui contrato de SLA
        if new_id.partner_id.sla_id:
            #Verifica se a categoria possui um SLA cadastrado
            category_response = self.env['website.support.sla.response'].search([('vsa_id','=',new_id.partner_id.sla_id.id), ('category_id','=',new_id.category.id)])
            if category_response:
                new_id.sla_id = new_id.partner_id.sla_id.id
                new_id.sla_active = True
                new_id.sla_timer = category_response.response_time
                new_id.sla_response_category_id = category_response.id

        #Envia um email para todos da categoria
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category')
        support_ticket_menu = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_menu')
        support_ticket_action = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_action')

        for my_user in new_id.category.cat_user_ids:
            values = notification_template.generate_email(new_id.id)
            values['body_html'] = values['body_html'].replace("_ticket_url_", "web#id=" + str(new_id.id) + "&view_type=form&model=website.support.ticket&menu_id=" + str(support_ticket_menu.id) + "&action=" + str(support_ticket_action.id) ).replace("_user_name_",  my_user.partner_id.name)
            values['email_to'] = my_user.partner_id.email

            send_mail = self.env['mail.mail'].create(values)
            send_mail.send()

            #Remove the message from the chatter since this would bloat the communication history by a lot
            send_mail.mail_message_id.res_id = 0

        return new_id

    @api.multi
    def write(self, values, context=None):

        update_rec = super(WebsiteSupportTicket, self).write(values)

        if 'state' in values:
            if self.state.mail_template_id:
                self.state.mail_template_id.send_mail(self.id, True)

        #Email user if category has changed
        if 'category' in values:
            change_category_email = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category_change')
            change_category_email.send_mail(self.id, True)

        if 'user_id' in values:
            setting_change_user_email_template_id = self.env['ir.default'].get('website.support.settings', 'change_user_email_template_id')

            if setting_change_user_email_template_id:
                email_template = self.env['mail.template'].browse(setting_change_user_email_template_id)
            else:
                #Default email template
                email_template = self.env['ir.model.data'].get_object('website_support','support_ticket_user_change')

            email_values = email_template.generate_email([self.id])[self.id]
            email_values['model'] = "website.support.ticket"
            email_values['res_id'] = self.id
            assigned_user = self.env['res.users'].browse( int(values['user_id']) )
            email_values['email_to'] = assigned_user.partner_id.email
            email_values['body_html'] = email_values['body_html'].replace("_user_name_", assigned_user.name)
            email_values['body'] = email_values['body'].replace("_user_name_", assigned_user.name)
            send_mail = self.env['mail.mail'].create(email_values)
            send_mail.send()


        return update_rec

    def send_survey(self):
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_survey')
        values = notification_template.generate_email(self.id)
        surevey_url = "support/survey/" + str(self.portal_access_key)
        values['body_html'] = values['body_html'].replace("_survey_url_",surevey_url)
        send_mail = self.env['mail.mail'].create(values)
        send_mail.send(True)

class WebsiteSupportTicketApproval(models.Model):

    _name = "website.support.ticket.approval"

    wst_id = fields.Many2one('website.support.ticket', string="Support Ticket")
    name = fields.Char(string="Name", translate=True)

class WebsiteSupportTicketField(models.Model):

    _name = "website.support.ticket.field"

    wst_id = fields.Many2one('website.support.ticket', string="Support Ticket")
    name = fields.Char(string="Label")
    value = fields.Char(string="Value")

class WebsiteSupportTicketMessage(models.Model):

    _name = "website.support.ticket.message"

    ticket_id = fields.Many2one('website.support.ticket', string='Ticket ID')
    by = fields.Selection([('staff','Staff'), ('customer','Customer')], string="By")
    content = fields.Html(string="Content")

class WebsiteSupportTicketCategories(models.Model):

    _name = "website.support.ticket.categories"
    _order = "sequence asc"
    _inherit = ['mail.alias.mixin', 'mail.thread', 'portal.mixin']

    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'website.support.ticket')

    def get_alias_values(self):
        values = super(WebsiteSupportTicketCategories, self).get_alias_values()
        values['alias_defaults'] = {'category': self.id}
        return values

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Category Name')
    cat_user_ids = fields.Many2many('res.users', string="Category Users")
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict", required=True)

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.categories')
        values['sequence']=sequence
        return super(WebsiteSupportTicketCategories, self).create(values)

class WebsiteSupportTicketSubCategories(models.Model):

    _name = "website.support.ticket.subcategory"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Sub Category Name')   
    parent_category_id = fields.Many2one('website.support.ticket.categories', required=True, string="Parent Category")
    additional_field_ids = fields.One2many('website.support.ticket.subcategory.field', 'wsts_id', string="Additional Fields")
 
    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.subcategory')
        values['sequence']=sequence
        return super(WebsiteSupportTicketSubCategories, self).create(values)

class WebsiteSupportTicketSubCategoryField(models.Model):

    _name = "website.support.ticket.subcategory.field"

    wsts_id = fields.Many2one('website.support.ticket.subcategory', string="Sub Category")
    name = fields.Char(string="Label", required="True")
    type = fields.Selection([('textbox','Textbox')], default="textbox", required="True", string="Type")

class WebsiteSupportTicketStates(models.Model):

    _name = "website.support.ticket.states"

    name = fields.Char(required=True, translate=True, string='State Name')
    mail_template_id = fields.Many2one('mail.template', domain="[('model_id','=','website.support.ticket')]", string="Mail Template")

class WebsiteSupportTicketPriority(models.Model):

    _name = "website.support.ticket.priority"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string="Priority Name")
    color = fields.Char(string="Color")

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.priority')
        values['sequence']=sequence
        return super(WebsiteSupportTicketPriority, self).create(values)

class WebsiteSupportTicketTag(models.Model):

    _name = "website.support.ticket.tag"

    name = fields.Char(required=True, translate=True, string="Tag Name")

class WebsiteSupportTicketUsers(models.Model):

    _inherit = "res.users"

    cat_user_ids = fields.Many2many('website.support.ticket.categories', string="Category Users")

class WebsiteSupportTicketCompose(models.Model):

    _name = "website.support.ticket.close"

    ticket_id = fields.Many2one('website.support.ticket', string="Ticket ID")
    message = fields.Text(string="Close Message")

    def close_ticket(self):

        self.ticket_id.close_time = datetime.datetime.now()

        #Also set the date for gamification
        self.ticket_id.close_date = datetime.date.today()

        diff_time = datetime.datetime.strptime(self.ticket_id.close_time, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(self.ticket_id.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        self.ticket_id.time_to_close = diff_time.seconds

        closed_state = self.env['ir.model.data'].sudo().get_object('website_support', 'website_ticket_state_staff_closed')

        #We record state change manually since it would spam the chatter if every 'Staff Replied' and 'Customer Replied' gets recorded
        message = "<ul class=\"o_mail_thread_message_tracking\">\n<li>State:<span> " + self.ticket_id.state.name + " </span><b>-></b> " + closed_state.name + " </span></li></ul>"
        self.ticket_id.message_post(body=message, subject="Ticket Closed by Staff")

        self.ticket_id.close_comment = self.message
        self.ticket_id.closed_by_id = self.env.user.id
        self.ticket_id.state = closed_state.id

        self.ticket_id.sla_active = False

        #Auto send out survey
        setting_auto_send_survey = self.env['ir.default'].get('website.support.settings', 'auto_send_survey')
        if setting_auto_send_survey:
            self.ticket_id.send_survey()

        closed_state_mail_template = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_closed').mail_template_id

        if closed_state_mail_template:
            closed_state_mail_template.send_mail(self.ticket_id.id, True)

class WebsiteSupportTicketCompose(models.Model):

    _name = "website.support.ticket.compose"

    ticket_id = fields.Many2one('website.support.ticket', string='Ticket ID')
    partner_id = fields.Many2one('res.partner', string="Partner", readonly="True")
    email = fields.Char(string="Email", readonly="True")
    subject = fields.Char(string="Subject", readonly="True")
    body = fields.Text(string="Message Body")
    template_id = fields.Many2one('mail.template', string="Mail Template", domain="[('model_id','=','website.support.ticket'), ('built_in','=',False)]")
    approval = fields.Boolean(string="Approval")
    planned_time = fields.Datetime(string="Planned Time")

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            values = self.env['mail.compose.message'].generate_email_for_composer(self.template_id.id, [self.ticket_id.id])[self.ticket_id.id]
            self.body = values['body']

    @api.one
    def send_reply(self):

        #Change the approval state before we send the mail
        if self.approval:
            #Change the ticket state to awaiting approval
            awaiting_approval_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_awaiting_approval')
            self.ticket_id.state = awaiting_approval_state.id

            #One support request per ticket...
            self.ticket_id.planned_time = self.planned_time
            self.ticket_id.approval_message = self.body
            self.ticket_id.sla_active = False

        #Send email
        values = {}

        setting_staff_reply_email_template_id = self.env['ir.default'].get('website.support.settings', 'staff_reply_email_template_id')

        if setting_staff_reply_email_template_id:
            email_wrapper = self.env['mail.template'].browse(setting_staff_reply_email_template_id)

        values = email_wrapper.generate_email([self.id])[self.id]
        values['model'] = "website.support.ticket"
        values['res_id'] = self.ticket_id.id
        send_mail = self.env['mail.mail'].create(values)
        send_mail.send()

        #Add to the message history to keep the data clean from the rest HTML
        self.env['website.support.ticket.message'].create({'ticket_id': self.ticket_id.id, 'by': 'staff', 'content':self.body.replace("<p>","").replace("</p>","")})

        #Post in message history
        #self.ticket_id.message_post(body=self.body, subject=self.subject, message_type='comment', subtype='mt_comment')

        if self.approval:
            #Also change the approval
            awaiting_approval = self.env['ir.model.data'].get_object('website_support','awaiting_approval')
            self.ticket_id.approval_id = awaiting_approval.id
        else:
            #Change the ticket state to staff replied
            staff_replied = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')
            self.ticket_id.state = staff_replied.id