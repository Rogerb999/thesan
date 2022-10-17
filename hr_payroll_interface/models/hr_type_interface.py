# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrTypeInterface(models.Model):
    """Hr Type Interface."""

    _name = 'hr.type.interface'
    _description = 'HrTypeInterface'

    @api.model
    def _get_formats(self):
        return self.env['ir.actions.report'].search(
            [('model', '=', 'hr.payroll.interface')]).ids

    name = fields.Char()
    from_draft_ids = fields.Many2many(
        'res.partner', 'hr_type_interface_from_draft_rel',
        'hr_type_interface_id', 'from_draft_id', string="From Draft", domain=[
            ('email', '!=', False)])
    from_done_ids = fields.Many2many(
        'res.partner', 'hr_type_interface_from_done_rel',
        'hr_type_interface_id', 'from_done_id', string="From Done", domain=[
            ('email', '!=', False)])

    formats_ids = fields.Many2many(
        'ir.actions.report', string="Formats",
        domain=[('model', '=', 'hr.payroll.interface')], default=_get_formats)
