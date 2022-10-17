# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Account(models.Model):
    """Added the payroll field in the account."""

    _inherit = "account.account"

    is_payroll = fields.Boolean('Payroll')
