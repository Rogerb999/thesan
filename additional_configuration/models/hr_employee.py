# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    birthday = fields.Date(
        'Date of Birth',
        groups="hr.group_hr_user,additional_configuration.group_you",
        track_visibility='onchange')
    country_of_birth = fields.Many2one(
        'res.country', string="Country of Birth",
        groups="hr.group_hr_user,additional_configuration.group_you",
        track_visibility='onchange')
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)',
        groups="hr.group_hr_user,additional_configuration.group_you",
        track_visibility='onchange')
    emergency_contact = fields.Char(
        "Emergency Contact",
        groups="hr.group_hr_user,additional_configuration.group_you",
        track_visibility='onchange')
    # private partner
    address_home_id = fields.Many2one(
        'res.partner', 'Private Address',
        help='Enter here the private address of the employee,'
             ' not the one linked to your company.',
        groups="hr.group_hr_user,additional_configuration.group_you",
        track_visibility='onchange')
