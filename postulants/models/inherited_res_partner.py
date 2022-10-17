# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import oauth2
import lxml.html
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    """Added the postulant details in the partner."""

    _inherit = "res.partner"

    postulant = fields.Boolean(track_visibility='always')
    first_name = fields.Char(string='First Name')
    second_name = fields.Char(string='Second Name')
    surname = fields.Char(string='Surname')
    second_surname = fields.Char(string='Second Surname')
    hr_applicant_ids = fields.One2many('hr.applicant', 'partner_id')
    referred_by_partner_id = fields.Many2one(
        'res.partner', string='Referred By')
    referred_channel_id = fields.Many2one(
        'hr.referred.channel', string='Referred Channel')
    state_selection = fields.Selection([
        ('eligible', 'Eligible'),
        ('not_eligible', 'Not Eligible'),
        ('in_process', 'In Process'),
        ('hired', 'Hired'),
    ], string='State Selection', default='eligible',
        copy=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    hr_cv_employee_id = fields.Many2one(
        'hr.cv.employee', string='Curriculum Vitae')

    @api.onchange('first_name', 'second_name', 'surname', 'second_surname')
    def onchange_name(self):
        name = "{0} {1} {2} {3}".format(
            self.surname or '',
            self.second_surname or '',
            self.first_name or '',
            self.second_name or '')
        self.name = re.sub("\s\s+", " ", name)

    @api.onchange('postulant')
    def _onchange_postulant(self):
        self.state_selection = ''
        if self.postulant:
            self.state_selection = 'eligible'

