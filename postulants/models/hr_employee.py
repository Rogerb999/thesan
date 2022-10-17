# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com`>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HrEmployee(models.Model):
    """Adds Extra Feature."""

    _inherit = "hr.employee"

    @api.onchange('gender')
    def onchange_gender(self):
        """Onchange to link Gender."""
        if self.gender and self.address_home_id:
            self.address_home_id.write({
                'gender': self.gender,
            })
