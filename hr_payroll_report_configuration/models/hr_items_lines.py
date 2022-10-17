# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrItemsLines(models.Model):
    """Hr Items Lines."""

    _name = "hr.items.lines"
    _description = "Hr Items Lines"
    # _rec_name = "account_id"

    name = fields.Char('Name')
    account_id = fields.Many2one('account.account', 'Account')
    partner_id = fields.Many2one('res.partner', 'Partner')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    other = fields.Char()
    assign_partner = fields.Selection(
        selection=[
            ("partner", "Partner"),
            ("employee", "Employee"),
            ("other", "Other")])
    group_rule_ids = fields.Many2many(
        'hr.group.rules',
        'hr_items_lines_hr_group_rules_default_rel',
        'hr_items_lines_id', 'hr_group_rules_id')
    group_value_id = fields.Many2many(
        'hr.group.values',
        'hr_items_lines_hr_group_values_default_rel',
        'hr_items_lines_id', 'hr_group_values_id')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Other value clean."""
        if self.partner_id:
            self.assign_partner = 'partner'

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """Other value clean."""
        if self.employee_id:
            self.assign_partner = 'employee'

    @api.onchange('other')
    def onchange_other(self):
        """Other value clean."""
        if self.other:
            self.assign_partner = 'other'

    @api.onchange('assign_partner')
    def onchange_assign_partner(self):
        """Other value clean."""
        if self.assign_partner:
            if self.assign_partner == 'partner':
                self.employee_id = False
                self.other = ''
            if self.assign_partner == 'employee':
                self.partner_id = False
                self.other = ''
            if self.assign_partner == 'other':
                self.employee_id = False
                self.partner_id = False
