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


class HRContractCompletion(models.Model):
    _inherit = "hr.contract.completion"
    
    @api.model
    def create(self, vals):
        res = super(HRContractCompletion, self).create(vals)
        res.action_webhook_werp_create_contract_completion_form_data(22, vals)
        return res
    
    @api.multi
    def action_webhook_werp_create_contract_completion_form_data(self, webhook_werp_type, vals):
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', self._name),
             ('url_type', '=', 'w_plan'),
             ('trigger', 'in', ['on_create', 'on_create_or_write'])])
        for webhook_werp_id in webhook_werp_ids:
            final_data = {
                'from': {},
                'to': {},
                'data': {},
                'webhook_werp_type': webhook_werp_type,
                'webhook_werp_history_id': {},
                'reference': '%s,%s' % (self._name, self.id)
            }

            identification_id = ""
            person_id = ""
            ident_type = ""
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
            contarct_id = self.env['hr.contract'].search([
                ('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
            json = {
                "EmployeeID":  self.employee_id.id,
                "PersonId": person_id,
                "Company": self.employee_id.company_id.name,
                "TerminationDate": str(self.date) or "",
                "FirstName": self.employee_id.address_home_id and self.employee_id.address_home_id.first_name or "",
                "LastName": self.employee_id.address_home_id and self.employee_id.address_home_id.surname or "",
                "MiddleInitial": self.employee_id.address_home_id and self.employee_id.address_home_id.second_name or "",
                "WorkEmail": self.employee_id.work_email or "",
                "NetworkID": "",
                "EmploymentEndDate": str(self.date) or "",
                "TermOfEmployment": contarct_id and contarct_id.type_id.name or "",
                "AxSetupType": "",
                "EmployeeType": "F" if self.employee_id.resource_calendar_id.fix_days else "P",
                "RequestDate": str(self.date) or "",
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
