# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrGroupValues(models.Model):
    """Hr Group Values."""

    _name = "hr.group.values"
    _description = "Hr Group Values"

    @api.depends('module_id', 'field_id')
    def _compute_name(self):
        for rec in self:
            rec.name = ''
            if rec.module_id and rec.field_id:
                rec.name = rec.module_id.name + ' - ' + rec.field_id.name

    name = fields.Char(compute="_compute_name")
    module_id = fields.Many2one('ir.model')
    field_id = fields.Many2one('ir.model.fields',
                               domain="[('model_id','=',module_id)]")
