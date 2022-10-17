# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)

ident_type = [
    ('rut', 'RUT'),
    ('id_document', 'Citizenship card'),
    ('id_card', 'Identity card'),
    ('passport', 'Passport'),
    ('foreign_id_card', 'Foreign Identity Card'),
    ('external_id', 'Exterior ID'),
    ('diplomatic_card', 'Diplomatic Card'),
    ('residence_document', 'Except for Permanence Conduct'),
    ('civil_registration', 'Civil registration'),
    ('national_citizen_id', 'Citizenship card'),
    ('NIT', 'N.I.T.'),
    ('external_NIT', 'Nit Immigration'),
    ('external_society_without_NIT', 'Foreign company without N.I.T. In colombia'),
    ('trust', 'Fideicomiso'),
    ('natural_person_NIT', 'Nit natural person')
]

jca_details_type = [
    ('Base', 'Base'),
    ('Strategic', 'Strategic'),
    ('Tactical', 'Tactical')
]


class ObjectConfg(models.Model):
    _name = 'object.confg'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", track_visibility='always')
    object_id = fields.Many2one(
        comodel_name="ir.model", string="Model", track_visibility='always')
    field_ids = fields.One2many(comodel_name='object.fields.confg',
                                inverse_name="object_confg_id",
                                string="Fields")
    url = fields.Char(string='URL', track_visibility='always')
    sequence = fields.Integer('Sequence', default=1, track_visibility='always')

    @api.multi
    def get_data(self, model_id):
        final_data = {'data': []}
        fields_ids = self.field_ids.filtered(
            lambda p: p.is_notification)
        rel_field = fields_ids.filtered(
            lambda p: p.is_relation)
        value = {}
        for rel in rel_field:
            if rel.sub_field_ids:
                value[rel.field_name] = {}
            main_sub_field = getattr(model_id, rel.field_name)
            for sub_field in rel.sub_field_ids:
                sub_id = getattr(main_sub_field, sub_field.name)
                if sub_field.ttype == 'selection':
                    if sub_field.name == 'ident_type':
                        value[rel.field_name][sub_field.name] = dict(ident_type).get(sub_id) or ''
                    elif sub_field.name == 'jca_details_type':
                        value[rel.field_name][sub_field.name] = dict(jca_details_type).get(sub_id) or ''
                    else:
                        selection_dict = dict(main_sub_field._fields[sub_field.name].selection)
                        value[rel.field_name][sub_field.name] = selection_dict.get(sub_id) or ''
                elif main_sub_field:
                    if isinstance(sub_id, (type(u''), bool, int, float, str)):
                        value[rel.field_name][sub_field.name] = sub_id or ''
                    else:
                        value[rel.field_name][sub_field.name] = sub_id.name or ''
            try:
                rel_id = getattr(model_id, rel.field_name).name
            except:
                rel_id = getattr(model_id, rel.field_name).id
            if rel.sub_field_ids:
                value[rel.field_name][rel.field_name] = rel_id
            else:
                value[rel.field_name] = rel_id or ''
        final_data['data'] = value
        s_fields = fields_ids.filtered(
            lambda p: not p.is_relation)
        s_fields_dict = {}
        for sf in s_fields:
            field_value = getattr(model_id, sf.field_name)
            if sf.field_type == 'selection':
                if sf.field_name == 'ident_type':
                    s_fields_dict[sf.field_name] = dict(ident_type).get(field_value) or ''
                else:
                    selection_dict = dict(model_id._fields[sf.field_name].selection)
                    s_fields_dict[sf.field_name] = selection_dict.get(field_value) or ''
            else:
                if isinstance(field_value, (datetime, date)):
                    s_fields_dict[sf.field_name] = field_value.isoformat() or ''
                else:
                    if sf.field_name == 'active':
                        s_fields_dict[sf.field_name] = field_value
                    else:
                        s_fields_dict[sf.field_name] = field_value or ''
        final_data['data'].update(s_fields_dict)
        return final_data

    @api.multi
    def get_data_common(self, model_id):
        final_data = {'data': []}
        fields_ids = self.field_ids.filtered(
            lambda p: p.is_notification)
        rel_field = fields_ids.filtered(
            lambda p: p.is_relation)
        value = {}
        for rel in rel_field:
            if rel.sub_field_ids:
                value[rel.field_name] = {}
            main_sub_fields = getattr(model_id, rel.field_name)
            main_sub_items = []
            for main_sub_field in main_sub_fields:
              main_sub_item = {}
              for sub_field in rel.sub_field_ids:
                sub_id = getattr(main_sub_field, sub_field.name)
                if sub_field.ttype == 'selection':
                    if sub_field.name == 'ident_type':
                        main_sub_item[sub_field.name] = dict(ident_type).get(sub_id) or ''
                    elif sub_field.name == 'jca_details_type':
                        main_sub_item[sub_field.name] = dict(jca_details_type).get(sub_id) or ''
                    else:
                        selection_dict = dict(main_sub_field._fields[sub_field.name]._description_selection(self.env))
                        main_sub_item[sub_field.name] = selection_dict.get(sub_id) or ''
                elif main_sub_field:
                    if isinstance(sub_id, (type(u''), bool, int, float, str)):
                        main_sub_item[sub_field.name] = sub_id or ''
                    elif 'default_code' in sub_id:
                        main_sub_item[sub_field.name] = {'code': sub_id.default_code, 'id': sub_id.id}
                    else:
                        main_sub_item[sub_field.name] = sub_id.id or ''
              main_sub_items.append(main_sub_item)

            try:
                rel_id = getattr(model_id, rel.field_name).name
            except:
                rel_id = getattr(model_id, rel.field_name).ids

            if len(main_sub_items) > 1:
                value[rel.field_name] = main_sub_items
            elif len(main_sub_items) == 1:
                value[rel.field_name] = main_sub_items[0]

            if not rel.sub_field_ids:
                value[rel.field_name] = rel_id or ''
        final_data['data'] = value
        s_fields = fields_ids.filtered(
            lambda p: not p.is_relation)
        s_fields_dict = {}
        for sf in s_fields:
            field_value = getattr(model_id, sf.field_name)
            if sf.field_type == 'selection':
                if sf.field_name == 'ident_type':
                    s_fields_dict[sf.field_name] = dict(ident_type).get(field_value) or ''
                else:
                    selection_dict = dict(model_id._fields[sf.field_name].selection)
                    s_fields_dict[sf.field_name] = selection_dict.get(field_value) or ''
            else:
                if isinstance(field_value, (datetime, date)):
                    s_fields_dict[sf.field_name] = field_value.isoformat() or ''
                else:
                    if sf.field_name == 'active':
                        s_fields_dict[sf.field_name] = field_value
                    else:
                        s_fields_dict[sf.field_name] = field_value or ''
        final_data['data'].update(s_fields_dict)
        return final_data


class Basewebhook_werpHistory(models.Model):
    _name = 'object.fields.confg'
    _description = 'Base webhook_werp History'

    object_confg_id = fields.Many2one(comodel_name="object.confg",
                                      string="Object")
    field_id = fields.Many2one(comodel_name="ir.model.fields",
                               string="Field", track_visibility='always')
    model_name = fields.Char(related='field_id.relation',
                             string="Model Name", track_visibility='always')
    field_name = fields.Char(related='field_id.name',
                             string="Field Name", track_visibility='always')
    field_type = fields.Selection(
        related='field_id.ttype',
        string="Field Type", track_visibility='always')
    is_relation = fields.Boolean(
        string="Relational", track_visibility='always')
    is_notification = fields.Boolean(
        string="Is Notification", default=True, track_visibility='always')
    sub_field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string="Sub Fields", track_visibility='always')

    @api.onchange('field_id')
    def onchange_field_id_change(self):
        if self.field_id.relation:
            self.is_relation = True
