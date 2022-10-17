# -*- encoding: utf-8 -*-

import base64
import xlrd
from odoo import api, fields, models


class HrEmployeeUpdateWizard(models.TransientModel):
    _name = 'hr.employee.update.wizard'

    excel_file = fields.Binary('Employee Excel Data', required=1)

    @api.multi
    def data_import(self):
        wb = xlrd.open_workbook(
            file_contents=base64.decodestring(self.excel_file))
        row_list = []
        last_sheet = wb.sheet_by_index(-1)
        # Will pick last sheet of the Excel Workbook
        for row in range(1, last_sheet.nrows):
            row_list.append(last_sheet.row_values(row))
        for employee_list in row_list:
            identification_id = macro_area = work_group =\
                function_excecuted = job = parent = parent_identification_id =\
                False
            if employee_list[1]:
                identification_id = str(int(employee_list[1]))
            if employee_list[3]:
                macro_area = str(employee_list[3])
            if employee_list[4]:
                work_group = str(employee_list[4])
            if employee_list[5]:
                function_excecuted = str(employee_list[5])
            if employee_list[6]:
                job = str(employee_list[6])
            if employee_list[7]:
                parent = str(employee_list[7])
            if employee_list[8]:
                parent_identification_id = str(int(employee_list[8]))
            if macro_area:
                macro_area_id = self.env['macro.area'].search(
                    [('name', 'ilike', macro_area)], limit=1)
                if not macro_area_id:
                    macro_area_id = self.env[
                        'macro.area'].create({'name': macro_area})
            if work_group:
                work_group_id = self.env['work.group'].search(
                    [('name', 'ilike', work_group)], limit=1)
                if not work_group_id:
                    work_group_id = self.env[
                        'work.group'].create({'name': work_group})
            if function_excecuted:
                function_executed_id = self.env['function.executed'].search(
                    [('name', 'ilike', function_excecuted)], limit=1)
                if not function_executed_id:
                    function_executed_id = self.env[
                        'function.executed'].create({
                            'name': function_excecuted})
            if job:
                hr_job_id = self.env['hr.job'].search(
                    [('name', 'ilike', job)], limit=1)
            if parent:
                parent_employee_id = self.env['hr.employee'].search(
                    [('name', 'ilike', parent)], limit=1)
                if parent_employee_id:
                    if parent_identification_id and\
                            parent_employee_id.identification_id !=\
                            parent_identification_id:
                        parent_employee_id.write({
                            'identification_id': parent_identification_id
                        })
            if identification_id:
                employee_id = self.env['hr.employee'].search(
                    [('identification_id', '=', identification_id)], limit=1)
                if employee_id:
                    if not employee_id.identification_id or\
                            employee_id.identification_id != identification_id:
                        employee_id.write({
                            'identification_id': identification_id,
                        })
                    if not employee_id.macro_area_id or\
                            employee_id.macro_area_id != macro_area_id:
                        employee_id.write({
                            'macro_area_id': macro_area_id.id or '',
                        })
                    if not employee_id.work_group_id or\
                            employee_id.work_group_id != work_group_id:
                        employee_id.write({
                            'work_group_id': work_group_id.id or '',
                        })
                    if not employee_id.function_executed_id or\
                            employee_id.function_executed_id !=\
                            function_executed_id:
                        employee_id.write({
                            'function_executed_id':
                            function_executed_id.id or ''
                        })
                    if not employee_id.job_id or\
                            employee_id.job_id != hr_job_id:
                        employee_id.write({
                            'job_id': hr_job_id.id,
                        })
                    if not employee_id.parent_id or\
                            employee_id.parent_id != parent_employee_id:
                        employee_id.write({
                            'parent_id': parent_employee_id.id,
                        })
