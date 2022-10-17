# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging
import threading
from odoo import models, fields, api, _
from datetime import date, datetime
_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def write(self, vals):
        old_vals = self.read(vals.keys())
        res = super(HrContract, self).write(vals)
        if vals and old_vals:
            self.action_webhook_werp_signed_contract(vals, old_vals[0])
        return res

    @api.model
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        res.action_webhook_werp_create_form_data(13, vals)
        return res

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
            'employee_id': self.employee_id.parent_id.id,
            'name': self.employee_id.parent_id.name,
            'email': self.employee_id.parent_id.work_email,
            'token': ''
        })
        final_data['from'].update({
            'employee_id': self.employee_id.id,
            'name': self.employee_id.name,
            'email': self.employee_id.work_email,
            'token': ''
        })
        read_data = self.read(vals.keys())[0]
        return final_data, read_data

    @api.multi
    def final_webhook_werp_details(self, webhook_werp_id, final_data, json_data,
                              cv_field_list, binary_field_list):
        object_confg = self.env['object.confg'].search([
            ('object_id.model', '=', 'hr.employee')], limit=1, order='sequence')
        config_data = object_confg.get_data(self.employee_id)
        if webhook_werp_id.url_type == 'other':
            del final_data['data']['normal_field']
            del final_data['data']['cv_fields']
            del final_data['data']['binary_field']
            if config_data.get('data').get('entry_date'):
                config_data['data']['entry_date'] = str(self.date_start)
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
            [('model_id.model', '=', self._name), ('trigger', 'in', ['on_create', 'on_create_or_write'])])
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

    @api.multi
    def action_webhook_werp_signed_contract(self, vals, old_vals):
        webhook_werp_ids = self.env['webhook_werp'].search([
            ('model_id.model', '=', self._name),
            ('trigger', 'in', ['on_write', 'on_create_or_write']),
            ('url_type', '=', 'you')])
        for webhook_werp_id in webhook_werp_ids:
            if not vals:
                continue
            webhook_werp_type_list = []
            if vals.get('signed_contract', False):
                webhook_werp_type_list.extend([9, 11])
                vals.pop('signed_contract', False)
                vals.pop('datas_fname', False)
            if vals:
                webhook_werp_type_list.extend([10, 12])
            updated_vals = {}
            for webhook_werp_type in webhook_werp_type_list:
                final_data = {
                    'from': {}, 'to': {}, 'data': [],
                    'webhook_werp_type': webhook_werp_type,
                    'default_data': json.loads(
                        webhook_werp_id.default_json or '{}'),
                    'webhook_werp_history_id': {},
                    'reference': '%s,%s' % (self._name, self.id)
                }
                parent = self.employee_id.parent_id
                current_employee = {
                    'employee_id': self.employee_id.id,
                    'name': self.employee_id.name,
                    'email': self.employee_id.work_email,
                    'token': ''
                }
                if webhook_werp_type in [9, 10]:
                    final_data['to'].update(current_employee)
                else:
                    if parent:
                        uid = self.env.user
                        final_data['to'].update({
                            'employee_id': parent.id or uid.employee_id.id,
                            'name': parent.name or uid.partner_id.name,
                            'email': parent.work_email or uid.partner_id.email,
                            'token': ''
                        })
                    final_data['from'].update(current_employee)

                if webhook_werp_type in [9, 11]:
                    final_data['data'] = {
                        'message': 'Contract (%s) signed by %s!' % (
                            self.name, self.employee_id.name)}
                else:
                    if updated_vals:
                        final_data['data'] = updated_vals
                    else:
                        vals.pop('signed_contract', False)
                        vals.pop('datas_fname', False)
                        final_update_vals = {}
                        read_data = self.read(vals.keys())[0]
                        json_data = []
                        for v_data in vals:
                            new_vals = read_data.get(v_data)
                            old_values = old_vals.get(v_data)
                            field_string = self._fields[v_data].string
                            if isinstance(new_vals, tuple):
                                change_value = {
                                    'old_value':
                                        old_values and old_values[1] or False,
                                    'new_value': new_vals[1]
                                }
                            else:
                                odv = False
                                ndv = False
                                if isinstance(old_vals.get(v_data),
                                              (datetime, date)):
                                    odv = old_vals.get(v_data).isoformat()
                                if isinstance(vals.get(v_data), (datetime, date)):
                                    ndv = vals.get(v_data).isoformat()
                                if isinstance(old_values, tuple):
                                    odv = old_values[1]
                                change_value = {
                                    'old_value': odv or old_vals.get(v_data),
                                    'new_value': ndv or vals.get(v_data)}
                            key_data = {'key': field_string,
                                        'value': change_value
                                        }
                            json_data.append(key_data)
                            final_update_vals.update(json_data)
                        updated_vals = json_data
                    final_data['data'] = updated_vals
                webhook_werp_history_id = \
                    self.env['webhook_werp.history'].action_webhook_werp_history_create(
                        final_data)
                if webhook_werp_history_id:
                    final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                    thread = threading.Thread(
                        target=webhook_werp_id.sent_data,
                        args=(webhook_werp_id.model_name, final_data, self))
                    thread.start()
