# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

BINARY_FIELD_LIST = [
    'support'
]


class HRCVLanguageEmployee(models.Model):
    """This Class is used to define fields
    and methods for HR CV Language Employee."""

    _name = "hr.cv.language.employee"
    _description = "HR CV Language Employee"
    _rec_name = 'language_id'

    language_id = fields.Many2one('hr.language')
    employee_id = fields.Many2one('hr.employee')
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    competition_id = fields.Many2one(
        'hr.competition.language', 'Competition Language')
    level_id = fields.Many2one(
        'hr.competition.level.language', 'Competition Level Language')
    name_support = fields.Char()
    support = fields.Binary()
    support_attachment_url = fields.Char("Support URL")
    active = fields.Boolean(default=True)
    description = fields.Text()

    @api.model
    def create(self, vals):
        res = super(HRCVLanguageEmployee, self).create(vals)
        attachment_obj = self.env['ir.attachment']
        for bin_field in BINARY_FIELD_LIST:
            if vals.get(bin_field, False):
                name = vals.get(
                    'name_support', '') if bin_field == 'support' else\
                    bin_field
                attachment_obj.create(dict(
                    name=name,
                    datas_fname=name,
                    datas=vals.get(bin_field, ''),
                    res_model='hr.cv.language.employee',
                    res_field=bin_field,
                    type='binary',
                    res_id=res.id
                ))
        return res

    @api.multi
    def write(self, vals):
        res = super(HRCVLanguageEmployee, self).write(vals)
        attachment_obj = self.env['ir.attachment']
        for bin_field in BINARY_FIELD_LIST:
            if vals.get(bin_field, False):
                name = vals.get(
                    'name_support', '') if bin_field == 'support' else\
                    bin_field
                attachment_obj.create(dict(
                    name=name,
                    datas_fname=name,
                    datas=vals.get(bin_field, ''),
                    res_model='hr.cv.language.employee',
                    res_field=bin_field,
                    type='binary',
                    res_id=self.id
                ))
        return res
