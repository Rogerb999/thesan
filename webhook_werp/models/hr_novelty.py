# -*- coding: utf-8 -*-

import logging
import threading
from odoo import models, api, _
import json
_logger = logging.getLogger(__name__)

ident_type_list = [('rut', 'NIT'),
     ('id_document', 'Cédula'),
     ('id_card', 'Tarjeta de Identidad'),
     ('passport', 'Pasaporte'),
     ('foreign_id_card', 'Cédula Extranjera'),
     ('external_id', 'ID del Exterior'),
     ('diplomatic_card', 'Carné Diplomatico'),
     ('residence_document', 'Salvoconducto de Permanencia'),
     ('civil_registration', 'Registro Civil'),
     ('national_citizen_id', 'Cédula de ciudadanía'),
     ('NIT', 'N.I.T.'),
     ('external_NIT', 'Nit Extranjería'),
     ('external_society_without_NIT',
      'Sociedad extranjera sin N.I.T. En Colombia'),
     ('trust', 'Fideicomiso'),
     ('natural_person_NIT', 'Nit persona natural')
]


class HrNovelty(models.Model):
    _inherit = "hr.novelty"

    @api.model
    def create(self, vals):
        res = super(HrNovelty, self).create(vals)
        if res:
            res.action_webhook_werp(1, False)
            return res

    @api.multi
    def action_webhook_werp(self, type, message):
        webhook_werp_ids = self.env['webhook_werp'].search([
            ('model_id.model', '=', self._name),
            ('trigger', 'in', ['on_write', 'on_create_or_write']),
            ('url_type', '=', 'you')])
        for webhook_werp_id in webhook_werp_ids:
            records, domain = webhook_werp_id._filter_post_export_domain(self)
            if not records:
                continue
            final_data = {
                'from': {}, 'to': {}, 'data': [],
                'webhook_werp_type': type,
                'default_data': json.loads(webhook_werp_id.default_json or '{}'),
                'webhook_werp_history_id': {},
                'reference': '%s,%s' % (self._name, self.id)
            }
            uid = self.env.user
            employee_id = False
            parent_id = self.employee_id.parent_id
            if parent_id and uid != parent_id:
                employee_id = self.employee_id.parent_id
            if not employee_id:
                employee_id = uid.employee_id
            parent_val_data = {
                'employee_id': employee_id.id or False,
                'emp_name': employee_id.name or uid.partner_id.name,
                'email': employee_id.work_email or uid.partner_id.email,
                'token': ''
            }
            child_val_data = {
                'employee_id': self.employee_id.id,
                'parent_name': self.employee_id.name,
                'email': self.employee_id.work_email,
                'token': ''
            }
            if message is True:
                limit = self.employee_id.parent_id.approval_limit or 5
                final_data['data'] = {
                    'message': 'You need to approve the pending novelty'
                               ' because it exceeds %s approval '
                               'limits!' % limit}
                final_data['to'].update(parent_val_data)
            else:
                if type == 1:
                    final_data['from'].update(child_val_data)
                    final_data['to'].update(parent_val_data)
                    object_confg = self.env['object.confg'].search([
                        ('object_id.model', '=', self._name)], limit=1, order='sequence')
                    config_data = object_confg.get_data(self)
                    final_data['data'] = config_data.get('data')
                elif type in [2, 3]:
                    final_data['from'].update(parent_val_data)
                    final_data['to'].update(child_val_data)
                    final_data['data'] = {'novelty': self.state,
                                          'novelty_name': self.name,
                                          'user': self.env.user.name,
                                          'event_id': self.event_id.name,
                                          'reject_reason': message}
                elif type == 102:
                    final_data['from'].update(parent_val_data)
                    final_data['to'].update(child_val_data)
                    identification_id = ""
                    person_id = ""
                    if self.employee_id.ident_type == 'id_document':
                        ident_type = 'CC'
                    elif self.employee_id.ident_type == 'foreign_id_card':
                        ident_type = 'CE'
                    else:
                        ident_type = dict(ident_type_list).get(self.employee_id.ident_type) or ''
                    if self.employee_id.identification_id:
                        identification_id = self.employee_id.identification_id
                    if ident_type and identification_id:
                        person_id = ident_type + identification_id
                    elif ident_type:
                        person_id = self.employee_id.ident_type
                    elif identification_id:
                        person_id = self.employee_id.identification_id
                    employee_id = person_id
                    json_d = {
                        "EmployeeID": employee_id,
                        "PersonId": person_id,
                        "FirstName": self.employee_id.address_home_id and self.employee_id.address_home_id.first_name or "",
                        "LastName": self.employee_id.address_home_id and self.employee_id.address_home_id.surname or "",
                    }
                    final_data['data'] = json_d
            if final_data['data']:
                webhook_werp_history_id = \
                    self.env['webhook_werp.history'].action_webhook_werp_history_create(
                        final_data)
                if webhook_werp_history_id:
                    final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                    thread = threading.Thread(
                        target=webhook_werp_id.sent_data,
                        args=(webhook_werp_id.model_name, final_data, self))
                    thread.start()
                    return True

    @api.multi
    def action_approve(self):
        res = super(HrNovelty, self).action_approve()
        self.with_context({'action_cancel': True}).action_webhook_werp(2, False)
        return res

    @api.multi
    def action_wait(self):
        res = super(HrNovelty, self).action_wait()
        parent = self.employee_id.parent_id
        if parent and parent.total_remaining_approve_novelty > \
                parent.approval_limit:
            self.action_webhook_werp(5, True)
        return res

    @api.multi
    def action_wait_comments(self):
        res = super(HrNovelty, self).action_wait_comments()
        parent = self.employee_id.parent_id
        if parent and parent.total_remaining_approve_novelty > \
                parent.approval_limit:
            self.action_webhook_werp(5, True)
        return res

    @api.multi
    def action_reject_for_you(self, data):
        self.write({
            'reject_reason': data,
            'state': 'rejected'})
        self.action_webhook_werp(3, data)

    @api.multi
    def action_cancel(self):
        self.action_webhook_werp(102, False)
        super(HrNovelty, self).action_cancel()


class NoveltyRejectWizard(models.TransientModel):
    _inherit = "hr.novelty.reject.wizard"

    @api.multi
    def confirm(self):
        active_id = self.env.context.get('active_id')
        novelty_id = self.env['hr.novelty'].browse(active_id)
        novelty_id.write({
            'reject_reason': self.reject_reason,
            'state': 'rejected'})
        novelty_id.action_webhook_werp(3, False)
