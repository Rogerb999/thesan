# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons.resource.models.resource import Intervals, float_to_time
from datetime import datetime
from pytz import timezone
from dateutil.rrule import rrule, DAILY


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    # --------------------------------------------------
    # Computation API
    # --------------------------------------------------
    def _attendance_intervals(self, start_dt, end_dt, resource=None):
        """ Return the attendance intervals in the given datetime range.
            The returned intervals are expressed in the resource's timezone.
        """
        assert start_dt.tzinfo and end_dt.tzinfo
        combine = datetime.combine
    
        # express all dates and times in the resource's timezone
        tz = timezone((resource or self).tz)
        start_dt = start_dt.astimezone(tz)
        end_dt = end_dt.astimezone(tz)
    
        # for each attendance spec, generate the intervals in the date range
        result = []
        for attendance in self.attendance_ids:
            if attendance.calendar_id.company_id.deduct_saturday_in_leave and attendance.dayofweek == '5':
                continue
            if attendance.calendar_id.company_id.deduct_sunday_in_leave and attendance.dayofweek == '6':
                continue

            start = start_dt.date()
            if attendance.date_from:
                start = max(start, attendance.date_from)
            until = end_dt.date()
            if attendance.date_to:
                until = min(until, attendance.date_to)
            weekday = int(attendance.dayofweek)
        
            for day in rrule(DAILY, start, until=until, byweekday=weekday):
                # attendance hours are interpreted in the resource's timezone
                dt0 = tz.localize(combine(day, float_to_time(attendance.hour_from)))
                dt1 = tz.localize(combine(day, float_to_time(attendance.hour_to)))
                result.append((max(start_dt, dt0), min(end_dt, dt1), attendance))
        return Intervals(result)
