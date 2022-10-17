# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class LanguageLevelDetails(models.Model):
    _name = "language.level.details"
    _description = 'Language Level Details'

    language_id = fields.Many2one('hr.language', 'Language')
    level_id = fields.Many2one(
        'hr.competition.level.language', 'Competition Level Language')
    novelty_id = fields.Many2one('hr.novelty', 'Novelty')
