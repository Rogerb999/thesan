# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com`>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    recruitment_reason_id = fields.Many2one('recruitment.reason',
                                            'Recruitment Reasons')
    salary = fields.Float()
    experience = fields.Text()
    observation = fields.Text()
    lang_id = fields.Many2one('res.lang', string="Language")
