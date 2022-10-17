# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com`>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RecruitmentReasons(models.Model):
    _name = "recruitment.reason"
    _description = 'Recruitment Reason'

    name = fields.Char('Name')
    description = fields.Text('Description')
    abbreviation = fields.Char('Abbreviation')
