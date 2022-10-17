# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrEmployee(models.Model):
    """Overwrite the Hr Employee."""

    _inherit = "hr.employee"

    hr_employee_work_group_ids = fields.One2many(
        'hr.employee.work.group', 'employee_id')


class HrEmployeeWorkGroup(models.Model):
    """Overwrite the Hr Employee Work Group."""

    _name = "hr.employee.work.group"
    _description = "Hr Employee Work Group"

    @api.depends('work_group_id', 'work_group_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.work_group_id and rec.work_group_id.name:
                rec.name = rec.work_group_id.name

    work_group_id = fields.Many2one('work.group')
    name = fields.Char(compute='_compute_name')
    secuence = fields.Integer()
    employee_id = fields.Many2one('hr.employee')

    @api.model
    def create(self, vals):
        """Sequence Insert."""
        record_count = self.env['hr.employee.work.group'].search_count([])
        vals.update({'secuence': record_count + 1})
        return super(HrEmployeeWorkGroup, self).create(vals)

    @api.multi
    def unlink(self):
        """Sequence Update."""
        for line in self:
            if line.secuence:
                for latest in self.env['hr.employee.work.group'].search(
                        [('secuence', '>', line.secuence)]):
                    latest.secuence -= 1
        return super(HrEmployeeWorkGroup, self).unlink()
