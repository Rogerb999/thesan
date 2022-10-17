# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import Warning


class HrNovelty(models.Model):
    """Hr Novelties."""
    _inherit = 'hr.novelty'

    after_close = fields.Boolean(string='After Close Novelties',
                                 track_visibility='onchange')

    @api.multi
    def action_cancel(self):
        current_date = fields.Date.today()
        last_date_of_month = datetime(current_date.year, current_date.month, 1
                                      ) + relativedelta(months=1, days=-1)
        close_id = self.env['close.event'].search([
            ('date_finish', '>', current_date),
            ('date_finish', '<', last_date_of_month),
            ('state', '=', 'confirmed')])
        if close_id:
            raise Warning(_('The action cancel must be before'
                            ' close payroll please contact payroll '
                            'staff to review this process'))
        return super(HrNovelty, self).action_cancel()

    @api.multi
    def create_leave(self):
        res = {}
        #'Integrate functionality register after close date payroll'
        res = super(HrNovelty, self).create_leave()
        tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
        date_start = fields.Date.today() + relativedelta(day=1)
        date_end = fields.Date.today() + relativedelta(
            months=+1, day=1, days=-1)
        close_id = self.env['close.event'].search([
            ('date_finish', '>', str(date_start)),
            ('date_finish', '<', str(date_end)),
            ('state', '=', 'confirmed')])
        if close_id and close_id.date_finish < fields.Date.today() and\
                self.start_date.month <= close_id.date_finish.month and\
                self.start_date.year <= close_id.date_finish.year:
            self.leave_id.write({'after_close': True})
        return res

    @api.multi
    def action_approve(self, boss_employee=False):
        res = super(HrNovelty, self).action_approve()
        date_start = fields.Date.today() + relativedelta(day=1)
        date_end = fields.Date.today() + relativedelta(
            months=+1, day=1, days=-1)
        close_id = self.env['close.event'].search([
            ('date_finish', '>', str(date_start)),
            ('date_finish', '<', str(date_end)),
            ('state', '=', 'confirmed')])
        if close_id and close_id.date_finish < fields.Date.today() and\
                self.start_date.month <= close_id.date_finish.month and\
                self.start_date.year <= close_id.date_finish.year:
            self.write({'after_close': True})
        return res
