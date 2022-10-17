# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_bp = fields.Boolean('BP')
    is_daf = fields.Boolean('DAF')
    is_adaf = fields.Boolean('ADAF')
    is_vp = fields.Boolean('VP')
