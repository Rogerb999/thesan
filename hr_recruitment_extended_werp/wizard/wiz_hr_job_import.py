# -*- encoding: utf-8 -*-

import base64
import xlrd
from odoo import api, fields, models


class WizHrJobImport(models.TransientModel):
    _name = 'wiz.hr.job.import'

    excel_file = fields.Binary('Payroll Excel Data', required=1)

    @api.multi
    def data_import(self):
        wb = xlrd.open_workbook(
            file_contents=base64.decodestring(self.excel_file))
        row_list = []
        last_sheet = wb.sheet_by_index(-1)
        # Will pick last sheet of the Excel Workbook
        for row in range(1, last_sheet.nrows):
            row_list.append(last_sheet.row_values(row))
        for job_list in row_list:
            macro_area = str(job_list[1])
            work_group = str(job_list[2])
            function_excecuted = str(job_list[3])
            name = str(job_list[4])
            if macro_area:
                macro_area_id = self.env['macro.area'].search(
                    [('name', '=', macro_area)], limit=1)
                if not macro_area_id:
                    macro_area_id = self.env[
                        'macro.area'].create({'name': macro_area})
            if work_group:
                work_group_id = self.env['work.group'].search(
                    [('name', '=', work_group)], limit=1)
                if not work_group_id:
                    work_group_id = self.env[
                        'work.group'].create({'name': work_group})
            if function_excecuted:
                function_executed_id = self.env['function.executed'].search(
                    [('name', '=', function_excecuted)], limit=1)
                if not function_executed_id:
                    function_executed_id = self.env[
                        'function.executed'].create({
                            'name': function_excecuted})
            if name:
                hr_job_id = self.env['hr.job'].search(
                    [('name', '=', name)], limit=1)
                if hr_job_id:
                    hr_job_id.write({
                        'macro_area_id': macro_area_id.id or '',
                        'work_group_id': work_group_id.id or '',
                        'function_executed_id': function_executed_id.id or ''
                    })
                if not hr_job_id:
                    hr_job_id.create({
                        'name': name,
                        'macro_area_id': macro_area_id.id or '',
                        'work_group_id': work_group_id.id or '',
                        'function_executed_id': function_executed_id.id or ''
                    })
