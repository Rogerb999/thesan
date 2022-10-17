# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

BINARY_FIELD_LIST = [
    'support'
]


class HRCVAcademicStudies(models.Model):
    """This Class is used to define fields
    and methods for HR CV Academic Studies."""

    _name = "hr.cv.academic.studies"
    _description = "HR CV Academic Studies"

    name = fields.Char()
    academic_institution_id = fields.Many2one('hr.academic.institution')
    academic_area_id = fields.Many2one('hr.academic.area')
    level_academic_id = fields.Many2one('hr.academic.level')
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([
        ('terminated', 'Terminated'),
        ('progress', 'In progress'),
        ('postpone', 'postpone'),
    ], "Academic State")
    type_education = fields.Selection([
        ('formal', 'Formal'),
        ('nonformal', 'Not Formal'),
    ])
    employee_id = fields.Many2one('hr.employee')
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one(
        'res.country.state', 'State',
        domain="[('country_id', '=', country_id)]")
    city_id = fields.Many2one(
        'res.city', 'City', domain="[('state_id', '=', state_id)]")
    name_support = fields.Char()
    support = fields.Binary()
    support_attachment_url = fields.Char("Support URL")
    active = fields.Boolean(default=True)
    description = fields.Text()

    @api.model
    def create(self, vals):
        res = super(HRCVAcademicStudies, self).create(vals)
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
                    res_model='hr.cv.academic.studies',
                    res_field=bin_field,
                    type='binary',
                    res_id=res.id
                ))
        return res

    @api.multi
    def write(self, vals):
        res = super(HRCVAcademicStudies, self).write(vals)
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
                    res_model='hr.cv.academic.studies',
                    res_field=bin_field,
                    type='binary',
                    res_id=self.id
                ))
        return res
