# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ResGroups(models.Model):
    _inherit = 'res.groups'

    # @api.model
    # def create(self, vals):
    #     if not self.env.context.get('group_create'):
    #         res = super(ResGroups, self).create(vals)
    #         self.env['hr.job'].with_context({'job_create': True}).create({'name': res.name, 'group_id': res.id})
    #         return res
    #     else:
    #         return super(ResGroups, self).create(vals)
