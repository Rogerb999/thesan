# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class Basewebhook_werpHistory(models.Model):
    _inherit = 'object.fields.confg'

    search_fields_config_id = fields.Many2one(
        comodel_name="search.fields.config",
        string="Object")


class SearchFieldsConfig(models.Model):
    _name = 'search.fields.config'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", track_visibility='always')
    sequence = fields.Integer('Sequence', default=1, track_visibility='always')
    object_id = fields.Many2one(
        comodel_name="ir.model", string="Model", track_visibility='always')
    field_ids = fields.One2many(comodel_name='object.fields.confg',
                                inverse_name="search_fields_config_id",
                                string="Fields")
    active = fields.Boolean('Active', default=True)

    @api.constrains('object_id')
    def _check_total_perc(self):
        for rec in self:
            if self.search([('object_id', '=', rec.object_id.id), ('id', '!=', rec.id)]):
                raise ValidationError(_("Model (%s) already configured. Please update exists"
                                        " model details!") % rec.object_id.name)

    @api.onchange('object_id')
    def onchange_object_id_change(self):
        if self.object_id:
            self.name = self.object_id.name


class SearchSubFieldsConfig(models.Model):
    _name = 'search.sub.fields.config'

    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", track_visibility='always')
    model_id = fields.Many2one(
        comodel_name="ir.model", string="Model", track_visibility='always')
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string="Fields")
    active = fields.Boolean('Active', default=True)

    @api.onchange('model_id')
    def onchange_model_id_change(self):
        if self.model_id:
            self.name = self.model_id.name

    @api.constrains('model_id')
    def _check_total_perc(self):
        for rec in self:
            if self.search([('model_id', '=', rec.model_id.id), ('id', '!=', rec.id)]):
                raise ValidationError(_("Model (%s) already configured. Please update exists"
                                        " model details!") % rec.model_id.name)
