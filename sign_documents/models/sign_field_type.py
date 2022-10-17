# -*- coding: utf-8 -*-

from odoo import models, fields


class SignFieldType(models.Model):
    _name = 'sign.field.type'
    _description = 'Sign Field Type'

    name = fields.Char('Name', required=True)
    sign_type = fields.Selection([
        ('signature', 'Signature'),
        ('name', 'Name'),
        ('text', 'Text'),
        ('initial', 'Initial'),
    ])
    height = fields.Float('Height')
    width = fields.Float('Width')
