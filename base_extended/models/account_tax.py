# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class AccountTax(models.Model):
    _inherit = "account.tax"

    iva_tax = fields.Boolean('IVA Tax')
