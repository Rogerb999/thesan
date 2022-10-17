# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com`>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrJob(models.Model):
    """Adds States Extra Values."""

    _inherit = "hr.job"

    state = fields.Selection(selection_add=[('pause', 'Pause'),
                                            ('canceled', 'Canceled')])
    hr_reason_changed_id = fields.Many2one('hr.reason.changed',
                                           string="Reason Changed")

    @api.multi
    def set_pause(self):
        """Set the Job Position in Pause State."""
        return self.write({
            'state': 'pause',
        })

    @api.multi
    def set_cancel(self):
        """Set the Job Position in Cancel State."""
        return self.write({
            'state': 'canceled',
        })
