# -*- coding: utf-8 -*-
# Copyright 2020 CorTex IT Solutions Ltd. (<https://cortexsolutions.net/>)
# License AGPL-3

from odoo import fields, models, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    move_line_ids = fields.One2many(related="move_id.line_ids", string="Journal Items",readonly=True,copy=False)

