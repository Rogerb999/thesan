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


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def write(self, vals):
        if vals.get('name', False) or vals.get('first_name', False) or vals.get('surname', False) or vals.get('street', False) or \
                vals.get('street2', False) or vals.get('city_id', False) or vals.get('state_id', False) or \
                vals.get('zip', False) or vals.get('country_id', False) or vals.get('phone', False) or \
                vals.get('function_id') or vals.get('title') or vals.get('l10n_co_document_type') or vals.get('vat'):
            self.action_webhook_werp_update_form_data_partner(20, vals)
        res = super(ResPartner, self).write(vals)
        return res

    @api.multi
    def get_generic_details(self, webhook_werp_type, vals):
        final_data = {
            'from': {},
            'to': {},
            'data': {},
            'webhook_werp_type': webhook_werp_type,
            'webhook_werp_history_id': {},
            'reference': '%s,%s' % (self._name, self.id)
        }
        read_data = self.read(vals.keys())[0]
        return final_data, read_data

    @api.multi
    def action_webhook_werp_update_form_data_partner(self, webhook_werp_type, vals):
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', 'res.partner'),
             ('url_type', '=', 'w_plan'),
             ('trigger', 'in', ['on_create', 'on_write', 'on_create_or_write'])])
        for webhook_werp_id in webhook_werp_ids:
            if vals:
                final_data, read_data = self.get_generic_details(
                    webhook_werp_type, vals)
            employee_id = self.env['hr.employee'].search([('address_home_id', '=', self.id)], limit=1)
            state_id = False
            country_id = False
            function_id = False
            title_id = False
            if vals.get('state_id'):
                state_id = self.env['res.country.state'].browse(vals['state_id'])
            if vals.get('country_id'):
                country_id = self.env['res.country'].browse(vals['country_id'])
            if vals.get('function_id'):
                function_id = self.env['hr.job'].browse(vals['function_id'])
            if vals.get('title'):
                title_id = self.env['res.partner.title'].browse(vals['title'])
            identification_id = ""
            person_id = ""
            if employee_id.ident_type == 'id_document':
                ident_type = 'CC'
            elif employee_id.ident_type == 'foreign_id_card':
                ident_type = 'CE'
            else:
                ident_type = dict(ident_type_list).get(employee_id.ident_type) or ''
            if employee_id.identification_id:
                identification_id = employee_id.identification_id
            if ident_type and identification_id:
                person_id = ident_type + identification_id
            elif ident_type:
                person_id = employee_id.ident_type
            elif identification_id:
                person_id = employee_id.identification_id
            json = {
                "EmployeeID":  employee_id.id,
                "Company": employee_id.company_id.name,
                "AxLegalEntity": employee_id.company_id.name,
                "PersonId": person_id,
                "Title": employee_id.job_id and employee_id.job_id.name or "",
                "FirstName": vals.get('first_name', self.first_name) or "",
                "LastName": vals.get('surname', self.surname) or "",
                "Street1": vals.get('street', self.street) or "",
                "Street2": vals.get('street2', self.street2) or "",
                "City": vals.get('city') or self.city or self.city_id.name or "",
                "State": state_id and state_id.name or self.state_id.name or "",
                "ZipCode": vals.get('zip', self.zip) or "",
                "Country": country_id and country_id.name or self.country_id.name or "",
                "Phone": vals.get('phone', self.phone) or "",
                "MiddleInitial": vals.get('second_name', self.second_name) or "",
                "NewValue": function_id and function_id.name or self.function_id.name or "",
                "FieldName": title_id and title_id.name or self.title.name or "",
            }
            if 'first_name' in vals:
                json.update({"OldFirstName": self.first_name or ""})
            if 'surname' in vals:
                json.update({"OldLastName": self.surname or ""})
            if 'second_name' in vals:
                json.update({"OldMiddleInitial": self.second_name or ""})
            if 'Street1' in vals:
                json.update({"OldStreet1": self.street or ""})
            if 'Street2' in vals:
                json.update({"OldStreet2": self.street2 or ""})
            if 'city' in vals:
                json.update({"OldCity": self.city or ""})
            if 'state_id' in vals:
                json.update({"OldState": self.state_id.name or ""})
            if 'zip' in vals:
                json.update({"OldZip": self.zip or ""})
            if 'country_id' in vals:
                json.update({"OldCountry": self.country_id.name or ""})
            if 'phone' in vals:
                json.update({"OldPhone": self.phone or ""})
            if 'function_id' in vals:
                json.update({"OldNewValue": self.function_id.name or ""})
            if 'title' in vals:
                json.update({"OldFieldName": self.title.name or ""})
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
