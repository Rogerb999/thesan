# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class HrContract(models.Model):
    """Hr Contract."""

    _inherit = 'hr.contract'

    recruitment_reason_id = fields.Many2one(
        'recruitment.reason',
        'Recruitment Reasons', copy=False)
