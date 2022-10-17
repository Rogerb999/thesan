# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class HrNoveltyJob(models.Model):
    """Hr Novelty Job."""

    _name = 'hr.novelty.job'
    _description = 'Novelty Job'
    _rec_name = 'job_id'

    novelty_id = fields.Many2one('hr.novelty', 'Novelty', copy=False)
    job_id = fields.Many2one('hr.job', 'Job')
    state = fields.Selection([('recruit', 'Recruitment in Progress'),
                              ('open', 'Not Recruitment'),
                              ('pause', 'Pause'),
                              ('canceled', 'Cancelled')],
                             default='recruit', copy=False)
    recruitment_reason_id = fields.Many2one('recruitment.reason',
                                            'Recruitment Reasons', copy=False)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee', copy=False)
