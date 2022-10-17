# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)
import pytz
from datetime import datetime
from pytz import timezone
fmt = "%Y-%m-%d %H:%M:%S"
Status = [
    ('pending', 'Pending'),
    ('ready', 'Ready'),
    ('progress', 'In Progress'),
    ('done', 'Finished'),
    ('cancel', 'Cancelled')]

class MailMessage(models.Model):
    _inherit = "mail.message"

    brand_id = fields.Many2one('multi.brand', 'Brand')

    def set_brands(self, values):
        brand_id = False
        if values.get('model') == 'sale.order':
            so_id = self.env['sale.order'].browse(values.get('res_id'))
            brand_id = so_id.opportunity_id.brand_id.id
        elif values.get('model') == 'crm.lead':
            cl_id = self.env['crm.lead'].browse(values.get('res_id'))
            brand_id = cl_id.brand_id.id
        elif values.get('model') == 'crm.lead.stage':
            cls_id = self.env['crm.lead.stage'].browse(values.get('res_id'))
            brand_id = cls_id.crm_lead_id.brand_id.id
        elif values.get('model') == 'mrp.workorder':
            mw_id = self.env['mrp.workorder'].browse(values.get('res_id'))
            brand_id = mw_id.brand_id.id
        elif values.get('model') == 'mrp.production':
            mp_id = self.env['mrp.production'].browse(values.get('res_id'))
            brand_id = mp_id.brand_id.id
        if brand_id:
            self.brand_id = brand_id
        return True

    @api.model
    def create(self, values):
        if values.get('model') == 'sale.order':
            so_id = self.env['sale.order'].browse(values.get('res_id'))
            values['brand_id'] = so_id.opportunity_id.brand_id.id
        elif values.get('model') == 'crm.lead':
            cl_id = self.env['crm.lead'].browse(values.get('res_id'))
            values['brand_id'] = cl_id.brand_id.id
        elif values.get('model') == 'crm.lead.stage':
            cls_id = self.env['crm.lead.stage'].browse(values.get('res_id'))
            values['brand_id'] = cls_id.crm_lead_id.brand_id.id
        elif values.get('model') == 'mrp.workorder':
            mw_id = self.env['mrp.workorder'].browse(values.get('res_id'))
            values['brand_id'] = mw_id.brand_id.id or mw_id.production_id.brand_id.id
        elif values.get('model') == 'mrp.production':
            mp_id = self.env['mrp.production'].browse(values.get('res_id'))
            values['brand_id'] = mp_id.brand_id.id or mp_id.lead_id.brand_id.id
        return super(MailMessage, self).create(values)

    def get_watcher_list(self):
        if self.model == 'workorder.comment':
            workorder_comment_id = self.env['workorder.comment'].search([('id', '=', self.res_id)])
            workorder_id = workorder_comment_id.order_id

        elif self.model == 'mrp.workcenter.productivity':
            productivity_id = self.env['mrp.workcenter.productivity'].search([('id', '=', self.res_id)])
            workorder_id = productivity_id.workorder_id
        else:
            workorder_id = self.env['mrp.workorder'].search([('id', '=', self.res_id)])
        email = workorder_id.watcher_ids.filtered(lambda line: line.id != self._context.get('uid', False)).mapped('login')
        e_l = str(email)[1:-1].replace("'", "")
        return e_l

    def get_workorder_data(self):
        workorder_id = self.env['mrp.workorder'].search([('id', '=', self.res_id)])
        if not workorder_id:
            return {
                'id': "",
                'url': "",
                'name': "",
                'assign_id': 'Not assigned',
                'responsible_id': 'Not assigned',
                'create_date': "",
                'status': "",
                'comments': "",
            }
        str_string = self.author_id.name + " updated "
        length = len(self.sudo().tracking_value_ids)
        count = 1
        for tracking_value_id in self.sudo().tracking_value_ids:
            values = ""
            if tracking_value_id.field_type == 'boolean':
                values = "False" if tracking_value_id.new_value_integer == 0 else "True"
            elif tracking_value_id.field_type == 'integer':
                values = tracking_value_id.new_value_integer or 0
            elif tracking_value_id.field_type in ['many2one', 'selection', 'char']:
                values = tracking_value_id.new_value_char or False
            elif tracking_value_id.field_type in ['datetime', 'date']:
                values = tracking_value_id.new_value_datetime or False
            elif tracking_value_id.field_type == 'float':
                values = tracking_value_id.new_value_float or 0.00
            elif tracking_value_id.field_type == 'monetary':
                values = tracking_value_id.new_value_monetary or 0.00
            elif tracking_value_id.field_type in ['text', 'html']:
                values = tracking_value_id.new_value_text or False
            if length == count:
                str_string += "\n" + tracking_value_id.field_desc + " to " + str(values) + " "
            else:
                str_string += "\n" + tracking_value_id.field_desc + " to " + str(values) + ","
            count += 1

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        brand_reference = str(workorder_id.production_id.brand_id.brand_reference) or ""
        lead_id = str(workorder_id.production_id.lead_id.id) or ""
        workorder_str = str(workorder_id.id)
        if url == 'https://stage-wsuiteerp.wsuite.com':
            final_url = "https://staging-project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" + workorder_str
        elif url == 'https://development-wsuiteerp.wsuite.com':
            final_url = "https://development-project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" + workorder_str
        elif url == 'https://wsuiteerp.wsuite.com':
            final_url = "https://project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" +workorder_str
        else:
            final_url = ""
        res = {
            'id': workorder_id.id,
            'url': final_url,
            'name': workorder_id.name,
            'assign_id': workorder_id.assign_id.name or 'Not assigned',
            'responsible_id': workorder_id.responsible_id.name or 'Not assigned',
            'create_date': self.get_timzone_date(workorder_id) or workorder_id.create_date,
            'status': dict(Status).get(workorder_id.state),
            'comments': str_string,
        }
        return res

    def get_timzone_date(self, workorder_id):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        tz_name = user.tz or 'UTC'
        date_utc = pytz.timezone('UTC').localize(workorder_id.create_date, is_dst=False)
        create_date = date_utc.astimezone(timezone(tz_name))
        return create_date.strftime(fmt)

    def get_workorder_comments_data(self):
        workorder_comment_id = self.env['workorder.comment'].search([('id', '=', self.res_id)])
        workorder_id = workorder_comment_id.order_id
        if not workorder_id:
            return {
                'id': "",
                'url': "",
                'name': "",
                'assign_id': 'Not assigned',
                'responsible_id': 'Not assigned',
                'create_date': "",
                'status': "",
                'comments': "",
            }
        str_string = self.author_id.name + " added/updated "
        length = len(self.sudo().tracking_value_ids)
        count = 1
        for tracking_value_id in self.sudo().tracking_value_ids:
            values = ""
            if tracking_value_id.field_type == 'boolean':
                values = "False" if tracking_value_id.new_value_integer == 0 else "True"
            elif tracking_value_id.field_type == 'integer':
                values = tracking_value_id.new_value_integer or 0
            elif tracking_value_id.field_type in ['many2one', 'selection', 'char']:
                values = tracking_value_id.new_value_char or False
            elif tracking_value_id.field_type in ['datetime', 'date']:
                values = tracking_value_id.new_value_datetime or False
            elif tracking_value_id.field_type == 'float':
                values = tracking_value_id.new_value_float or 0.00
            elif tracking_value_id.field_type == 'monetary':
                values = tracking_value_id.new_value_monetary or 0.00
            elif tracking_value_id.field_type in ['text', 'html']:
                values = tracking_value_id.new_value_text or False
            if length == count:
                str_string += "\n" + tracking_value_id.field_desc + " to " + str(values) + " "
            else:
                str_string += "\n" + tracking_value_id.field_desc + " to " + str(values) + ","
            count += 1

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        brand_reference = str(workorder_id.production_id.brand_id.brand_reference) or ""
        lead_id = str(workorder_id.production_id.lead_id.id) or ""
        workorder_str = str(workorder_id.id)
        if url == 'https://stage-wsuiteerp.wsuite.com':
            final_url = "https://staging-project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" + workorder_str
        elif url == 'https://development-wsuiteerp.wsuite.com':
            final_url = "https://development-project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" + workorder_str
        elif url == 'https://wsuiteerp.wsuite.com':
            final_url = "https://project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" +workorder_str
        else:
            final_url = ""
        res = {
            'id': workorder_id.id,
            'url': final_url,
            'name': workorder_id.name,
            'assign_id': workorder_id.assign_id.name or 'Not assigned',
            'responsible_id': workorder_id.responsible_id.name or 'Not assigned',
            'create_date': self.get_timzone_date(workorder_id) or workorder_id.create_date,
            'status': dict(Status).get(workorder_id.state),
            'comments': str_string,
        }
        return res

    def get_workorder_log_data(self):
        productivity_id = self.env['mrp.workcenter.productivity'].search([('id', '=', self.res_id)])
        workorder_id = productivity_id.workorder_id
        if not workorder_id:
            return {
                'id': "",
                'url': "",
                'name': "",
                'assign_id': 'Not assigned',
                'responsible_id': 'Not assigned',
                'create_date': "",
                'status': "",
                'comments': "",
            }
        str_string = self.author_id.name + " added "
        length = len(self.sudo().tracking_value_ids)
        if length == 2:
            str_string += "\n log hours " + str(self.sudo().tracking_value_ids[0].new_value_float) + " minutes with comment: " + str(
                self.sudo().tracking_value_ids[1].new_value_text)
        elif self.sudo().tracking_value_ids and self.sudo().tracking_value_ids[0].field == 'duration':
            str_string += "\n log hours " + str(self.sudo().tracking_value_ids[0].new_value_float) + " minutes."
        elif self.sudo().tracking_value_ids and self.sudo().tracking_value_ids[0].field == 'description':
            str_string += "\n comment: " + str(self.sudo().tracking_value_ids[0].new_value_text)

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        brand_reference = str(workorder_id.production_id.brand_id.brand_reference) or ""
        lead_id = str(workorder_id.production_id.lead_id.id) or ""
        workorder_str = str(workorder_id.id)
        if url == 'https://stage-wsuiteerp.wsuite.com':
            final_url = "https://staging-project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" + workorder_str
        elif url == 'https://development-wsuiteerp.wsuite.com':
            final_url = "https://development-project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" + workorder_str
        elif url == 'https://wsuiteerp.wsuite.com':
            final_url = "https://project.wsuite.com/" + brand_reference + "/projects/" + lead_id + "/work-packages/" +workorder_str
        else:
            final_url = ""
        res = {
            'id': workorder_id.id,
            'url': final_url,
            'name': workorder_id.name,
            'assign_id': workorder_id.assign_id.name or 'Not assigned',
            'responsible_id': workorder_id.responsible_id.name or 'Not assigned',
            'create_date': self.get_timzone_date(workorder_id) or workorder_id.create_date,
            'status': dict(Status).get(workorder_id.state),
            'comments': str_string,
        }
        return res