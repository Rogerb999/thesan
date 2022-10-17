# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ReasonDisqualification(models.Model):
    """This Class is used to define fields and
    methods for Reason Disqualification."""

    _name = "reason.disqualification"
    _description = "Reason Disqualification"

    name = fields.Char('Name')
    description = fields.Text('Description')
