# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRReasonChanged(models.Model):
    """This Class is used to define fields
    and methods for HR Reason Changed."""

    _name = "hr.reason.changed"
    _description = "HR Reason Changed"

    name = fields.Char()
    description = fields.Text()
