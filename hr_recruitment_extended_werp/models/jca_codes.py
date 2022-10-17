# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class JCADetails(models.Model):
    _name = "jca.details"
    _description = "JCA Details"

    name = fields.Char('Name')
    code = fields.Char('Code')
    type_of_level = fields.Selection([
        ('Base', 'Base'),
        ('Strategic', 'Strategic'),
        ('Tactical', 'Tactical')], 'Type of Level')
    description = fields.Text('Description')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = '[' + record.type_of_level + '] ' + name
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        domain = [('company_id', '=', self.env.user.company_id.id)]
        args = args or []
        if self.env.context.get('application_id', False):
            hr_applicant_id = self.env['hr.applicant'].browse(
                self.env.context['application_id'])
            if hr_applicant_id.job_id.jca_details_id:
                domain = [('id', '=',
                           hr_applicant_id.job_id.jca_details_id.id)]
        jac_ids = self.search(domain + args, limit=limit)
        return jac_ids.name_get()
