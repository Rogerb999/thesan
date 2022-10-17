# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

DateTimeFormat = '%Y-%m-%d %H:%M:%S'


class RecordStartStopTimer(models.Model):
    _name = "record.start.stop.timer"

    @api.depends(
        'start_stop_line_ids',
        'start_stop_line_ids.start_time',
        'start_stop_line_ids.stop_time'
    )
    def _compute_total_duration(self):
        for line in self:
            line.total_duration = sum(p.duration for p in line.start_stop_line_ids)

    @api.depends('start_time', 'stop_timer')
    def _compute_duration_str(self):
        for line in self:
            if line.start_time and line.stop_timer:
                start = datetime.strptime(str(line.start_time), DateTimeFormat)
                end = datetime.strptime(str(line.stop_timer), DateTimeFormat)
                diff = relativedelta(end, start)
                result = """{day} day {hour} hour {minute} min {second} sec""".format(
                    day=diff.days and diff.days or 0, hour=diff.hours
                     and diff.hours or 0,
                    minute=diff.minutes and diff.minutes or 0, second=diff.seconds
                    and diff.seconds or 0)
                line.duration_str = result

    start_time = fields.Datetime(
        string='Start Time',
        copy=False,
    )
    stop_timer = fields.Datetime(
        string='Stop Time',
        copy=False,
    )
    total_duration = fields.Float(
        string='Duration(Hours)',
        compute="_compute_total_duration",
        store=True,
    )
    duration_str = fields.Char(
        string="Duration",
        compute="_compute_duration_str"
    )
    start_stop_line_ids = fields.One2many(
        'record.start.stop.timer.lines',
        'parent_id',
        string='Pause Lines',
    )
    start_user_id = fields.Many2one(
        'res.users',
        string="Started By",
        copy=False,
        readonly=True,
    )
    stop_user_id = fields.Many2one(
        'res.users',
        string="Stopped By",
        copy=False,
        readonly=True,
    )
