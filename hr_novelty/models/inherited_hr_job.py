# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class HrJob(models.Model):
    """Hr Job."""

    _inherit = 'hr.job'

    hr_novelty_job_ids = fields.One2many('hr.novelty.job', 'job_id')
