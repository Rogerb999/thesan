# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    after_close = fields.Boolean(string='After Close Novelties',
                                 track_visibility='onchange')
