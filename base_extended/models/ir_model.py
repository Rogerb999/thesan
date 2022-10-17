# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random
from odoo import models, fields, api
users_image_list = [
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/albatross.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/clown-fish.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/crab.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/dolphin.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/fish.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/pelican.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/penguin.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/seahorse.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/swallow.png',
    'https://s3.amazonaws.com/production-assets.wsuite.com/default_user_images/turtle.png',
]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_default_img(self):
        index = random.randrange(0, len(users_image_list) - 1)
        url = users_image_list[index]
        return url

    profile_image_url = fields.Char(default=get_default_img)


class IrModel(models.Model):
    _inherit = "ir.model"

    wdev_name = fields.Char('Wdev Name')


class ResUsers(models.Model):
    _inherit = "res.users"

    auto_creation = fields.Boolean('Create Default Employee/Contract?')

    @api.multi
    def write(self, vals):
        active = vals.get('active')
        if active is False:
            email = vals.get('login') or self.login
            employee_id = self.env['hr.employee'].search([('work_email', '=', email)])
            if email:
                self.active_or_inactive_user(False, email)
            if employee_id:
                employee_id.active = False
        elif active is True:
            email = vals.get('login') or self.login
            employee_id = self.env['hr.employee'].search([('work_email', '=', email)])
            if not employee_id:
                employee_id = self.env['hr.employee'].search([('work_email', '=', email), ('active', '=', False)])
                if employee_id:
                    employee_id.active = True
            if email:
                self.active_or_inactive_user(True, email)
        return super(ResUsers, self).write(vals)

    @api.multi
    def _is_import_user(self):
        self.ensure_one()
        return self.has_group('base_extended.group_import_files')

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        res.partner_id.email = res.login
        if self.env.user.company_id.auto_creation:
            employee_id = self.env['hr.employee'].search([
                ('work_email', '=', res.login),
                ('active', 'in', [True, False])
            ], limit=1)
            if not employee_id:
                work_group_id = self.env['work.group'].search([('name', '=', res.operation_zone)], limit=1)
                employee_id = self.employee_id.create({
                    'name': res.name,
                    'user_id': res.id,
                    'address_home_id': res.partner_id.id,
                    'work_email': res.login,
                    'job_id': res.job_profile_id.id,
                    'work_group_id': work_group_id and work_group_id.id,
                    })
                self.env['hr.contract'].create({
                    'name': employee_id.name,
                    'employee_id': employee_id.id,
                    'wage': 0.0,
                    'state': 'open'
                    })
            res.write({'employee_id': employee_id.id})
        return res

    @api.multi
    def user_update_employee_data(self, user_id):
        if user_id and self.env.user.company_id.auto_creation:
            res_user_id = self.browse(user_id)
            if not res_user_id.employee_id:
                employee_id = self.env['hr.employee'].search([
                    ('work_email', '=',  res_user_id.login),
                    ('active', 'in', [True, False])], limit=1)
                if not employee_id:
                    work_group_id = self.env['work.group'].search([('name', '=', res_user_id.operation_zone)], limit=1)
                    employee_id = self.env['hr.employee'].create({
                        'name': res_user_id.name,
                        'user_id': res_user_id.id,
                        'address_home_id': res_user_id.partner_id.id,
                        'work_email': res_user_id.login,
                        'job_id': res_user_id.job_profile_id.id,
                        'work_group_id': work_group_id and work_group_id.id,
                    })
                    self.env['hr.contract'].create({
                        'name': employee_id.name,
                        'employee_id': employee_id.id,
                        'wage': 0.0,
                        'state': 'open'
                    })
                    res_user_id.with_context({'set_employee_details': True}).write({'employee_id': employee_id.id})
                elif employee_id:
                    if res_user_id.job_profile_id:
                        self._cr.execute('UPDATE hr_employee SET job_id=%s WHERE id=%s',
                                         (res_user_id.job_profile_id.id, employee_id.id))
                    if res_user_id.operation_zone:
                        work_group_id = self.env['work.group'].search([
                            ('name', '=', res_user_id.operation_zone)], limit=1)
                        if work_group_id:
                            self._cr.execute('UPDATE hr_employee SET work_group_id=%s WHERE id=%s',
                                             (work_group_id and work_group_id.id or False, employee_id.id))
                    res_user_id.with_context({'set_employee_details': True}).write({
                        'employee_id': employee_id.id,
                    })
            elif res_user_id.employee_id:
                if res_user_id.job_profile_id:
                    self._cr.execute('UPDATE hr_employee SET job_id=%s WHERE id=%s', (
                        res_user_id.job_profile_id.id, res_user_id.employee_id.id))
                if res_user_id.operation_zone:
                    work_group_id = self.env['work.group'].search([('name', '=', res_user_id.operation_zone)], limit=1)
                    if work_group_id:
                        self._cr.execute('UPDATE hr_employee SET work_group_id=%s WHERE id=%s',
                                         (work_group_id and work_group_id.id or False, res_user_id.employee_id.id))
        return True


class ResGroups(models.Model):
    _inherit = 'res.groups'

    qty_users = fields.Integer(compute='_compute_total_user_count', string='Total User')
    permission_json = fields.Text('Permission Json')
    cost_per_hour = fields.Float('Cost Per Hour')
    active_group = fields.Boolean('Active', default=True)

    def _compute_total_user_count(self):
        for record in self:
            record.qty_users = len(record.users)


class ResCompany(models.Model):
    _inherit = "res.company"

    company_slug = fields.Char('Company Slug')
    profit_percentage = fields.Float('Profit %')
    can_be_modified = fields.Boolean('Can be modified')
    stripe_company_id = fields.Char('Stripe Company Id')
    code_reference = fields.Char()
    auto_creation = fields.Boolean('Create Default Employee/Contract?')
    create_default_employee = fields.Boolean('Create Default Employee?')
    client_label = fields.Char('Client Label')
    brand_label = fields.Char('Brand Label')
    final_subject = fields.Char('Final Subject')
