# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HRStagePerc(models.Model):
    _name = 'hr.stage.perc'
    _description = 'HR Stage Percentage'
    _rec_name = 'stage_id'

    percentage = fields.Float()
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', required=True)
    hr_job_id = fields.Many2one('hr.job', 'Job')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_pause', 'In Pause'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')], 'State', required=True)
