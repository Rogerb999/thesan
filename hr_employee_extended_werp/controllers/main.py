# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import pycompat
import io
import operator
import json


class EmployeeExport(http.Controller):

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    @http.route(['/export/employee/<int:wizard_id>'],
                type='http', auth="public", website=True)
    def page(self, wizard_id=None, **kw):
        w_id = request.env['report.employee.wizard'].browse(wizard_id)
        model_name = w_id.model_name
        Model = request.env[model_name]
        if w_id.field_ids:
            fnames = w_id.field_ids.mapped('name')
            fields = dict(sorted(
                Model.fields_get(fnames).items()))
        else:
            fields = Model.fields_get()

        fields_list = []
        for f in fields:
            label = fields.get(f).get('string')
            fields_list.append({"name": f, "label": label})
            for sub_field in w_id.model_id.sub_model_field_ids:
                field_id = sub_field.field_id
                ResModel = request.env[field_id.relation]
                subfield_name = sub_field.sub_field_ids.mapped('name')
                resfields = dict(sorted(
                    ResModel.fields_get(subfield_name).items()))
                if field_id.name == f and field_id.ttype == 'many2one':
                    for res_f in resfields:
                        ah_name = f + '/' + res_f
                        ah_label = \
                            label + '/' + resfields.get(res_f).get('string')
                        fields_list.append({
                            "name": ah_name, "label": ah_label
                        })
                elif field_id.name == f and field_id.ttype in \
                        ['one2many', 'many2many']:
                    for o2m_f in resfields:
                        o2m_name = f + '/' + o2m_f
                        o2m_label = \
                            label + '/' + resfields.get(o2m_f).get('string')
                        fields_list.append({
                            "name": o2m_name, "label": o2m_label
                        })
        list_ids = w_id.employee_ids.ids
        if model_name == 'res.partner':
            list_ids = w_id.contact_ids.ids
        data = """{
            "model": """ + json.dumps(model_name) + """,
            "fields": """ + json.dumps(fields_list) + """,
            "ids": """ + str(list_ids) + """,
            "domain": [],
            "context": {"tz": "Asia/Kolkata", "lang": "en_US", "uid": 2},
            "import_compat": false}"""
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids',
                                'domain', 'import_compat')(params)
        Model = request.env[model].with_context(
            import_compat=import_compat, **params.get('context', {}))
        records = Model.browse(ids) or Model.search(
            domain, offset=0, limit=False, order=False)

        if not Model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']
        field_names = [f['name'] for f in fields]
        import_data = records.export_data(field_names, False).get('datas', [])

        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]
        return request.make_response(
            self.from_data_csv(columns_headers, import_data),
            headers=[('Content-Disposition',
                      content_disposition(self.filename(model, '.csv'))),
                     ('Content-Type', self.content_type)])

    def filename(self, base, type):
        return base + type

    def from_data_csv(self, fields, rows):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        writer.writerow(fields)

        for data in rows:
            row = []
            for d in data:
                # Spreadsheet apps tend to detect
                # formulas on leading =, + and -
                if isinstance(d, pycompat.string_types
                              ) and d.startswith(('=', '-', '+')):
                    d = "'" + d

                row.append(pycompat.to_text(d))
            writer.writerow(row)
        return fp.getvalue()
