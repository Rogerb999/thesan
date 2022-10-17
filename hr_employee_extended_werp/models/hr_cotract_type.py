# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrCotractType(models.Model):
    """HrCotractType."""

    _name = 'hr.cotract.type'
    _description = 'Hr Cotract Type'

    name = fields.Char()
    description = fields.Text()
