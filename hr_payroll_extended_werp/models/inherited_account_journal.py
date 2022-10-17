# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    """Added payroll boolean in journal."""

    _inherit = "account.journal"

    is_payroll = fields.Boolean('Payroll')
