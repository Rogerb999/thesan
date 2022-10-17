# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import base64
import csv
import io

from odoo import models, api, fields, _


class CreateContractIdentificationWizard(models.TransientModel):
    _name = "create.contract.identification.wizard"
    _description = "Create Contract Identification Wizard"

    file = fields.Binary('Upload CSV file')

    def create_contract(self):
        """Create contract from CSV."""
        for rec in self:
            csv_data = base64.b64decode(rec.file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)
            if file_reader:
                for data in file_reader[1:]:
                    if data[0]:
                        employee_rec = False
                        partner_rec_rec = self.env['res.partner'].search(
                            [('vat', '=', data[0])], limit=1)
                        if partner_rec_rec:
                            employee_rec = self.env['hr.employee'].search(
                                [('address_home_id', '=', partner_rec_rec.id)],
                                limit=1)
                        if employee_rec:
                            contract = self.env['hr.contract'].create({
                                'name': data[2] or '',
                                'employee_id': employee_rec.id,
                                'department_id':
                                employee_rec.department_id.id or '',
                                'job_id': employee_rec.job_id.id or '',
                                'wage': data[5] or ''})
                            if data[3]:
                                contract.write(
                                    {'date_start': datetime.datetime.strptime(
                                        data[3], "%m/%d/%Y").date()})
                            if data[4]:
                                contract.write(
                                    {'date_end': datetime.datetime.strptime(
                                        data[4], "%m/%d/%Y").date()})
                    if not data[0] and data[1]:
                        employee_rec = self.env['hr.employee'].search(
                            [('name', '=', data[1])], limit=1)
                        if employee_rec:
                            contract = self.env['hr.contract'].create({
                                'name': data[2] or '',
                                'employee_id': employee_rec.id,
                                'department_id':
                                employee_rec.department_id.id or '',
                                'job_id': employee_rec.job_id.id or '',
                                'wage': data[5] or ''})
                            if data[3]:
                                contract.write(
                                    {'date_start': datetime.datetime.strptime(
                                        data[3], "%m/%d/%Y").date()})
                            if data[4]:
                                contract.write(
                                    {'date_end': datetime.datetime.strptime(
                                        data[4], "%m/%d/%Y").date()})
