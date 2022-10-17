# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReportEmployeeWizard(models.TransientModel):
    _name = 'report.employee.wizard'
    _description = 'Report Employee Wizard'

    employee_ids = fields.Many2many(
        'hr.employee', 'employee_report_wizard_rel', string='Employees')
    contact_ids = fields.Many2many(
        'res.partner', 'contact_report_wizard_rel', string='Contacts')
    model_id = fields.Many2one(
        comodel_name="report.model.config", string="Model")
    original_model_id = fields.Many2one(
        comodel_name="ir.model", string="Original Model")
    model_name = fields.Char(string='Model Name')
    field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Fields")
    report_type = fields.Selection([
        ('csv', 'CSV')], default='csv')

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.field_ids = [(6, 0, [])]
        self.employee_ids = [(6, 0, [])]
        self.contact_ids = [(6, 0, [])]
        self.model_name = False
        self.original_model_id = False
        if self.model_id:
            self.model_name = self.model_id.model_id.model
            self.original_model_id = self.model_id.model_id.id
            field_ids = self.model_id.field_ids.mapped('id')
            self.update({'field_ids': [(6, 0, field_ids)]})

    @api.multi
    def action_export_data(self):
        if not self.field_ids:
            raise ValidationError(_('Please select any Fields!'))
        if self.model_name == 'hr.employee' and not self.employee_ids:
            raise ValidationError(_('Please select any Employees!'))
        elif self.model_name == 'res.partner' and not self.contact_ids:
            raise ValidationError(_('Please select any Contacts!'))
        return {
            'type': 'ir.actions.act_url',
            'name': "Employee Export Data",
            'target': 'self',
            'url': '/export/employee/%d' % self.id,
            'tag': 'reload',
        }
