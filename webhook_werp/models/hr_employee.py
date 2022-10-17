# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
import json
import logging
import threading
from datetime import date, datetime
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

agency_type_list = [
    ('production', 'Production'),
    ('media', 'Media'),
    ('creative', 'Creativity'),
    ('financial', 'Financial'),
    ('automotive', 'Automotive'),
    ('real_state', 'Real State'),
    ('client', 'Client'),
    ('other', 'Other'),
]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    approval_limit = fields.Integer(
        'Approval Limit', default=5, track_visibility='onchange')
    response_message = fields.Text(
        'Response Message', track_visibility='always')
    response_time = fields.Datetime(
        'Response Datetime', track_visibility='always')

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        res.action_webhook_werp_create_form_data(8, vals)
        if vals.get('parent_id', False):
            res.action_webhook_werp(7, False)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('address_home_id') or vals.get('bank_account_id'):
            self.action_webhook_werp_form_data_WPLAN(21, vals)
        if vals.get('address_home_id') or vals.get('work_email') or vals.get('name'):
            self.action_webhook_werp_form_data_AXSetup(104, vals)
        if vals.get('email', False):
            vals['work_email'] = vals.pop('email')
        if self._context.get('resume', False):
            return super(HrEmployee, self).write(vals)
        old_vals = self.read(vals.keys())
        check_method_call = False
        if vals:
            check_method_call = True
            check_update_data = False
            for k, v in vals.items():
                if old_vals and vals.get(k) != old_vals[0].get(k):
                    check_update_data = True
                    break
            if check_update_data:
                self.action_webhook_werp_form_data(
                    8, vals, old_vals and old_vals[0])
        if vals.get('parent_id', False):
            self.action_webhook_werp(7, False)
        if not check_method_call:
            return super(HrEmployee, self).write(vals)
        return True

    @api.multi
    def get_generic_details(self, webhook_werp_type, vals):
        final_data = {
            'from': {},
            'to': {},
            'data': {
                'normal_field': [],
                'cv_fields': [],
                'binary_field': [],
                'config_field': [],
            },
            'webhook_werp_type': webhook_werp_type,
            'webhook_werp_history_id': {},
            'reference': '%s,%s' % (self._name, self.id)
        }
        final_data['to'].update({
            'employee_id': self.parent_id.id,
            'name': self.parent_id.name,
            'email': self.parent_id.work_email,
            'token': ''
        })
        final_data['from'].update({
            'employee_id': self.id,
            'name': self.name,
            'email': self.work_email,
            'token': ''
        })
        skip_field_list = [
            'hr_employee_acumulate_ids', 'contact_reference_ids',
            'policy_ids', 'deductions_ids',
        ]
        for field in skip_field_list:
            vals.pop(field, False)
        read_data = self.read(vals.keys())[0]
        return final_data, read_data

    @api.multi
    def final_webhook_werp_details(self, webhook_werp_id, final_data, json_data,
                              cv_field_list, binary_field_list):
        object_confg = self.env['object.confg'].search([
            ('object_id.model', '=', self._name)], limit=1, order='sequence')
        config_data = object_confg.get_data(self)
        if webhook_werp_id.url_type == 'other':
            final_data['data']['normal_field'] = json_data
            del final_data['data']['cv_fields']
            del final_data['data']['binary_field']
            final_data['data']['config_field'] = config_data.get('data')
            final_data['webhook_werp_type'] = 13
        else:
            final_data['data']['normal_field'] = json_data
            final_data['data']['cv_fields'] = cv_field_list
            final_data['data']['binary_field'] = binary_field_list
        webhook_werp_history_id = \
            self.env['webhook_werp.history'].action_webhook_werp_history_create(
                final_data)
        if webhook_werp_history_id:
            final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
            thread = threading.Thread(
                target=webhook_werp_id.sent_data,
                args=(webhook_werp_id.model_name, final_data, self))
            thread.start()

    @api.multi
    def action_webhook_werp_create_form_data(self, webhook_werp_type, vals):
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', self._name),
             ('url_type', 'in', ['you', 'other']),
             ('trigger', 'in', ['on_create', 'on_create_or_write'])])
        for webhook_werp_id in webhook_werp_ids:
            if webhook_werp_id and vals:
                final_data, read_data = self.get_generic_details(
                    webhook_werp_type, vals)
                json_data = []
                cv_field_list = []
                binary_field_list = []
                for v_data in vals:
                    field_string = self._fields[v_data].string
                    if self._fields[v_data].type == 'one2many':
                        cv_field_list.append(field_string)
                        continue
                    if self._fields[v_data].type == 'binary':
                        binary_field_list.append(field_string)
                        continue
                    new_vals = read_data.get(v_data)
                    if isinstance(new_vals, tuple):
                        change_value = {
                            'old_value': False,
                            'new_value': new_vals[1]
                        }
                    else:
                        new_date_values = False
                        if isinstance(vals.get(v_data), (datetime, date)):
                            new_date_values = vals.get(v_data).isoformat()
                        change_value = {
                            'old_value': False,
                            'new_value': new_date_values or vals.get(v_data)}
                    if any(change_value.values()):
                        key_data = {'key': field_string,
                                    'value': change_value
                                    }
                        json_data.append(key_data)
                self.final_webhook_werp_details(webhook_werp_id, final_data, json_data,
                                           cv_field_list, binary_field_list)
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', self._name),
             ('url_type', '=', 'w_plan'),
             ('trigger', 'in', ['on_create', 'on_create_or_write'])])
        for webhook_werp_id in webhook_werp_ids:
            if vals:
                final_data, read_data = self.get_generic_details(
                    webhook_werp_type, vals)
            identification_id = ""
            person_id = ""
            if self.ident_type == 'id_document':
                ident_type = 'CC'
            elif self.ident_type == 'foreign_id_card':
                ident_type = 'CE'
            else:
                ident_type = dict(ident_type_list).get(self.ident_type) or ''
            if self.identification_id:
                identification_id = self.identification_id
            if ident_type and identification_id:
                person_id = ident_type + identification_id
            elif ident_type:
                person_id = self.ident_type
            elif identification_id:
                person_id = self.identification_id
            employee_id = person_id
            if self.address_home_id.agency_type:
                employee_id = dict(agency_type_list).get(self.address_home_id.agency_type) + '_' + person_id
            contarct_id = self.env['hr.contract'].search([
                ('employee_id', '=', self.id), ('state', '=', 'open')], limit=1)
            json = {
                "EmployeeID":  employee_id,
                "PersonId": person_id,
                "AxLegalEntity": self.company_id.name,
                "Company": self.company_id.name,
                "FirstName": self.address_home_id and self.address_home_id.first_name or "",
                "LastName": self.address_home_id and self.address_home_id.surname or "",
                "MiddleInitial": self.address_home_id and self.address_home_id.second_name or "",
                "WorkEmail": self.work_email or "",
                "NetworkID": "",
                "DisplayName": self.name or "",
                "Title": self.job_id and self.job_id.name or "",
                "EmploymentStartDate": str(self.entry_date) or "",
                "EmploymentEndDate": "",
                "TermOfEmployment": contarct_id and contarct_id.type_id.name or "",
                "EmployeeStatus": "A" if self.active else "I",
                "EmployeeType": "F" if self.resource_calendar_id.fix_days else "P",
                "Street1": self.address_home_id and self.address_home_id.street or "",
                "Street2": self.address_home_id and self.address_home_id.street2 or "",
                "City": self.address_home_id and self.address_home_id.city_id.name or "",
                "State": self.address_home_id and self.address_home_id.state_id.name or "",
                "ZipCode": self.address_home_id.zip or "",
                "Country": self.address_home_id.country_id.name or "",
                "Phone": self.address_home_id.phone or "",
                "EOBankName": self.bank_account_id and self.bank_account_id.bank_id.name or "",
                "EOBankAccountNumber": self.bank_account_id and self.bank_account_id.acc_number or "",
                "EOBankNameOnAccount":  self.bank_account_id and self.bank_account_id.acc_holder_name or "",
                "EOBankRoutingNumber": "",
                "EOBankType": self.bank_account_id and self.bank_account_id.type or ""
            }
            final_data['data'] = json
            webhook_werp_history_id = \
                self.env['webhook_werp.history'].action_webhook_werp_history_create(
                    final_data)
            if webhook_werp_history_id:
                final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                thread = threading.Thread(
                    target=webhook_werp_id.sent_data,
                    args=(webhook_werp_id.model_name, final_data, self))
                thread.start()

    @api.multi
    def action_webhook_werp_form_data(self, webhook_werp_type, vals, old_vals):
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', self._name),
             ('url_type', 'in', ['you', 'other']),
             ('trigger', 'in', ['on_write', 'on_create_or_write'])])
        self.with_context(resume=True).write(vals)
        for webhook_werp_id in webhook_werp_ids:
            if webhook_werp_id.url_type == 'other':
                if webhook_werp_id.check_active_deactive and 'active' not in vals:
                    continue
                if 'active' in vals and not webhook_werp_id.check_active_deactive:
                    continue
            if webhook_werp_id and vals:
                final_data, read_data = self.get_generic_details(
                    webhook_werp_type, vals)
                json_data = []
                cv_field_list = []
                binary_field_list = []
                for v_data in vals:
                    field_string = self._fields[v_data].string
                    if self._fields[v_data].type == 'one2many':
                        cv_field_list.append(field_string)
                        continue
                    if self._fields[v_data].type == 'binary':
                        binary_field_list.append(field_string)
                        continue
                    new_vals = read_data.get(v_data)
                    old_values = old_vals.get(v_data)
                    if isinstance(new_vals, tuple):
                        change_value = {
                            'old_value': old_values and old_values[1] or False,
                            'new_value': new_vals[1]
                        }
                    else:
                        old_date_values = False
                        new_date_values = False
                        if isinstance(old_vals.get(v_data), (datetime, date)):
                            old_date_values = old_vals.get(v_data).isoformat()
                        if isinstance(vals.get(v_data), (datetime, date)):
                            new_date_values = vals.get(v_data).isoformat()
                        if isinstance(old_values, tuple):
                            old_date_values = old_values[1]
                        change_value = {
                            'old_value': old_date_values or old_vals.get(v_data),
                            'new_value': new_date_values or vals.get(v_data)}
                    if any(change_value.values()):
                        key_data = {'key': field_string,
                                    'value': change_value
                                    }
                        json_data.append(key_data)
                self.final_webhook_werp_details(webhook_werp_id, final_data, json_data,
                                           cv_field_list, binary_field_list)

    @api.multi
    def action_webhook_werp_form_data_WPLAN(self, webhook_werp_type, vals):
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', self._name),
             ('url_type', '=', 'w_plan'),
             ('trigger', 'in', ['on_write', 'on_create_or_write'])])
        for webhook_werp_id in webhook_werp_ids:
            if vals:
                final_data, read_data = self.get_generic_details(
                    webhook_werp_type, vals)
            identification_id = ""
            person_id = ""
            if self.ident_type == 'id_document':
                ident_type = 'CC'
            elif self.ident_type == 'foreign_id_card':
                ident_type = 'CE'
            else:
                ident_type = dict(ident_type_list).get(self.ident_type) or ''
            if self.identification_id:
                identification_id = self.identification_id
            if ident_type and identification_id:
                person_id = ident_type + identification_id
            elif ident_type:
                person_id = self.ident_type
            elif identification_id:
                person_id = self.identification_id
            employee_id = person_id
            if self.address_home_id.agency_type:
                employee_id = dict(agency_type_list).get(self.address_home_id.agency_type) + '_' + person_id
            json = {
                "RequestId": self.id,
                "EmployeeID":  employee_id or "",
                "PersonId": person_id,
                "Company": self.company_id.name,
                "LegalEntity": self.company_id.name,
                "AxLegalEntity": self.company_id.name,
            }
            if vals.get('address_home_id'):
                partner_id = self.env['res.partner'].browse(vals['address_home_id'])
                json.update({
                    "OldFirstName": self.address_home_id.first_name or "",
                    "OldLastName": self.address_home_id.surname or "",
                    "OldMiddleInitial": self.address_home_id.second_name or "",
                    "OldNewValue": self.address_home_id.function_id.name or "",
                    "OldFieldName": self.address_home_id.title.name or "",
                    "FirstName": partner_id.first_name or "",
                    "LastName": partner_id.surname or "",
                    "MiddleInitial": partner_id.second_name or "",
                    "NewValue": partner_id.function_id.name or "",
                    "FieldName": partner_id.title.name or "",
                })
            if vals.get('bank_account_id'):
                partner_id = False
                if vals.get('address_home_id'):
                    partner_id = self.env['res.partner'].browse(vals['address_home_id'])
                bank_account_id = self.env['res.partner.bank'].browse(vals['bank_account_id'])
                json.update({
                    "EOBankName": bank_account_id.bank_id.name or "",
                    "EOBankAccountNumber": bank_account_id.acc_number or "",
                    "EOBankNameOnAccount": bank_account_id.acc_holder_name or "",
                    "EOBankType": bank_account_id.type or "",
                    "EOBankRoutingNumber": "",
                    "OldEOBankName": self.bank_account_id.bank_id.name or "",
                    "OldEOBankAccountNumber": self.bank_account_id.acc_number or "",
                    "OldEOBankNameOnAccount": self.bank_account_id.acc_holder_name or "",
                    "OldEOBankType": self.bank_account_id.type or "",
                    "FirstName": partner_id and partner_id.first_name or self.address_home_id.first_name or "",
                    "LastName": partner_id and partner_id.surname or self.address_home_id.surname or "",
                })
            final_data['data'] = json

            webhook_werp_history_id = \
                self.env['webhook_werp.history'].action_webhook_werp_history_create(
                    final_data)
            if webhook_werp_history_id:
                final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                thread = threading.Thread(
                    target=webhook_werp_id.sent_data,
                    args=(webhook_werp_id.model_name, final_data, self))
                thread.start()

    @api.multi
    def action_webhook_werp_form_data_AXSetup(self, webhook_werp_type, vals):
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', self._name),
             ('url_type', '=', 'other'),
             ('trigger', 'in', ['on_write', 'on_create_or_write'])])
        for webhook_werp_id in webhook_werp_ids:
            if vals:
                final_data, read_data = self.get_generic_details(
                    webhook_werp_type, vals)
            identification_id = ""
            person_id = ""
            if self.ident_type == 'id_document':
                ident_type = 'CC'
            elif self.ident_type == 'foreign_id_card':
                ident_type = 'CE'
            else:
                ident_type = dict(ident_type_list).get(self.ident_type) or ''
            if self.identification_id:
                identification_id = self.identification_id
            if ident_type and identification_id:
                person_id = ident_type + identification_id
            elif ident_type:
                person_id = self.ident_type
            elif identification_id:
                person_id = self.identification_id
            employee_id = person_id
            json = {
                "EmployeeID": employee_id or "",
                "PersonId": person_id,
                "AxLegalEntity": self.company_id.name,
                "NetworkID": "",
            }
            if vals.get('address_home_id'):
                partner_id = self.env['res.partner'].browse(vals['address_home_id'])
                json.update({
                    "FirstName": partner_id.first_name or "",
                    "LastName": partner_id.surname or "",
                })
            else:
                json.update({
                    "FirstName": self.address_home_id.first_name or "",
                    "LastName": self.address_home_id.surname or "",
                })

            if vals.get('work_email'):
                json.update({
                    "WorkEmail":vals.get('work_email') or "",
                })
            else:
                json.update({
                    "WorkEmail": self.work_email or "",
                })

            if vals.get('name') or vals.get('display_name'):
                json.update({
                    "DisplayName": vals.get('name') or vals.get('display_name') or "",
                })
            else:
                json.update({
                    "DisplayName": self.name or self.display_name or "",
                })
            final_data['data'] = json

            webhook_werp_history_id = \
                self.env['webhook_werp.history'].action_webhook_werp_history_create(
                    final_data)
            if webhook_werp_history_id:
                final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                thread = threading.Thread(
                    target=webhook_werp_id.sent_data,
                    args=(webhook_werp_id.model_name, final_data, self))
                thread.start()

    @api.multi
    def action_webhook_werp(self, type, message):
        webhook_werp_ids = self.env['webhook_werp'].search([
            ('model_id.model', '=', self._name),
            ('trigger', 'in', ['on_write', 'on_create_or_write']),
            ('url_type', '=', 'you')])
        for webhook_werp_id in webhook_werp_ids:
            final_data = {'from': {}, 'to': {}, 'data': [],
                          'webhook_werp_type': type,
                          'default_data': json.loads(
                              webhook_werp_id.default_json or '{}'),
                          'webhook_werp_history_id': {},
                          'reference': '%s,%s' % (self._name, self.id)
                          }
            parent_id = self.parent_id
            final_data['to'].update(
                {'employee_id': parent_id.id,
                 'parent_name': parent_id.name,
                 'email': parent_id.work_email,
                 'token': ''})
            final_data['data'] = {'parent_name': parent_id.name,
                                  'child_name': self.name
                                  }
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
