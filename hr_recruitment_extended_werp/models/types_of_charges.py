# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class TypesOfCharges(models.Model):
    """Different Types Of Charges."""

    _name = "types.of.charges"
    _description = "Types Of Charges"

    name = fields.Char()
    nivel = fields.Char()
