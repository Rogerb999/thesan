# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

DateTimeFormat = '%Y-%m-%d %H:%M:%S'


class RecordStartStopTimerLines(models.Model):
    _name = "record.start.stop.timer.lines"
    
    @api.depends('start_time', 'stop_time')
    def _compute_duration(self):
        for line in self:
            if line.start_time and line.stop_time:
                start = datetime.strptime(str(line.start_time), DateTimeFormat)
                end = datetime.strptime(str(line.stop_time), DateTimeFormat)
                print ("******start****end***********",start,end)
                diff = relativedelta(end, start)

                duration_hour = diff.hours
                if diff.days:
                    print ("::::::::days::::::::::::")
                    duration_hour = duration_hour + diff.days * 24.0

                if diff.minutes:
                    print ("::::::::minutes::::::::::::")
                    duration_hour = duration_hour + diff.minutes / 60.0

                if diff.seconds:
                    print ("::::::::seconds::::::::::::",duration_hour,diff.seconds)
                    duration_hour = duration_hour + diff.seconds / 360.0

                print (">>>>>>>>>>>>>>>>>>>>>>>>>>",duration_hour)
                line.duration = duration_hour

    start_time = fields.Datetime(
        string='Start Time',
        copy=False,
        readonly=True,
    )
    stop_time = fields.Datetime(
        string='Stop Time',
        copy=False,
        readonly=True,
    )
    parent_id = fields.Many2one(
        'record.start.stop.timer',
        string='Parent',
    )
    duration = fields.Float(
        string="Duration(Hours)",
        compute="_compute_duration",
        store=True,
    )
    pause_user_id = fields.Many2one(
        'res.users',
        string="Paused By",
        copy=False,
        readonly=True,
    )
    restart_user_id = fields.Many2one(
        'res.users',
        string="Restarted By",
        copy=False,
        readonly=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
