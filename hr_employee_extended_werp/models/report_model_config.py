# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ReportModelConfig(models.Model):
    _name = 'report.model.config'
    _description = 'Report Model Config'

    name = fields.Char(string="Name", related='model_id.name')
    model_id = fields.Many2one(
        comodel_name="ir.model", string="Model",
        domain=[('model', 'in', ['hr.employee', 'res.partner'])]
    )
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string="Fields")
    sub_model_field_ids = fields.One2many(
        comodel_name='report.sub.model.field.config',
        inverse_name="model_id",
        string="Sub Fields")


class ReportSubModelFieldConfig(models.Model):
    _name = 'report.sub.model.field.config'
    _description = 'Report Sub Model Field Config'

    model_id = fields.Many2one(
        comodel_name="report.model.config",
        string="Model")
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field")
    model_name = fields.Char(
        related='field_id.relation',
        string="Model Name")
    sub_field_ids = fields.Many2many(
        'ir.model.fields',
    )
