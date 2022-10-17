# -*- coding: utf-8 -*-
from collections import OrderedDict

from datetime import datetime

from odoo import http, _
from odoo.http import request
from odoo import fields
from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager


class WebsiteTaskSign(http.Controller):

    @http.route(['/record_signature'], type='json', auth="user", website=True)
    def record_signature(self, **kw):
        record_id = kw.get("res_id", False)
        record_model = kw.get('res_model', 'project.task')
        if kw.get("signature", False) and record_id and record_model:
            record = request.env[record_model].sudo().browse(int(record_id))
            record.sudo().write({'signature':kw.get("signature")})
        return True


class CustomerPortal(CustomerPortal):

    @http.route(['/record/work_time'], type='json', auth="user", website=True)
    def record_work_time(self, **kw):
        record_id = kw.get("record_id")
        record_type = kw.get("record_type")
        record_model = kw.get('record_model', 'project.record_id')

        record_time = fields.Datetime.now()
        print ("**********************",record_time)
        pause_obj = http.request.env['record.start.stop.timer.lines'].sudo()
        record_obj = request.env[record_model].sudo()
        record = record_obj.browse(record_id)
        url = False

        if record_id:
            if record_type == 'start':
                vals = {
                    'start_time': record_time,
                    'start_user_id': request._uid,
                    'start_stop_line_ids': [(0, 0, {
                        'start_time': record_time,
                        'restart_user_id': request._uid,
                    })]
                }
                record.write({'last_pause_time': False,
                            'start_stop_ids': [(0, 0, vals)]})
            else:
                start_line = False
                start_lines = record.start_stop_ids.sorted(reverse=True)
                if start_lines:
                    start_line = start_lines[0]
                if start_line:

                    if record_type in ['pause', 'stop']:
                        l2_domain = [
                            ('start_time', '!=', False),
                            ('stop_time', '=', False),
                            ('parent_id', '=', start_line.id)
                        ]
                        l2_start_line = pause_obj.search(l2_domain, order="start_time desc",limit=1)
                        if l2_start_line:
                            l2_start_line.write({
                                'stop_time': record_time,
                                'pause_user_id': request._uid,
                            })

                        if record_type == 'stop':
                            start_line.write({
                                'stop_timer': record_time,
                                'stop_user_id': request._uid,
                            })
                            record.write({
                                'last_pause_time': False
                            })
                            task = False
                            if record_model == 'project.task':
                                task =  record
                            elif record_model == 'helpdesk.support':
                                task = record.task_id

                            if task:
                                today = fields.Date.today()
                                total_duration = start_line.total_duration
                                total_duration = '{0:02.0f}:{1:02.0f}'.format(*divmod(total_duration * 60, 60))

                                split_start_time = start_line.start_time.split(' ')[1].split(':')
                                start_time = split_start_time[0] + ":"+ split_start_time[1]
                                split_end_time = start_line.stop_timer.split(' ')[1].split(':')
                                end_time = split_end_time[0] + ":" + split_end_time[1]

                                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                timesheet_url =\
                                    "/my/add_timesheet?timesheet_date=%s&start_time=%s&end_time=%s&project=%s&task=%s&duration=%s" %(
                                        today, start_time, end_time, task.project_id.id, task.id, total_duration
                                    )
                                url = base_url + timesheet_url
                        else:
                            record.write({
                                'last_pause_time': record_time
                            })
                    elif record_type == 'restart':
                        vals = {
                            'start_time': record_time,
                            'restart_user_id': request._uid,
                        }
                        start_line.write({'start_stop_line_ids': [(0, 0, vals)]})
                        record.write({
                            'last_pause_time': False,
                        })
        if url:
            return {'url': url}
        else:
            return {}
