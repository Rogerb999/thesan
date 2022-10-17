# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    novelty_ref = fields.Char(
        'Novelty Reference',
        copy=False, readonly=True)
    is_eps = fields.Boolean(string='EPS')
    is_arl = fields.Boolean(string='ARL')
