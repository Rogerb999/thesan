# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    slug = fields.Char('Slug')
    sort_name = fields.Char('Sort Name')
    stripe_token = fields.Char('Stripe Token')
    stripe_id = fields.Char('Stripe Id')
    card_brand = fields.Char('Card Brand')
    card_last_four = fields.Char('Card Last Four')
    trial_ends_at = fields.Char('Trial Ends At')
    transaction_id = fields.Char('Transaction Id')
    wpartner_id = fields.Many2one('res.partner', 'W-Partner')
    autoretention = fields.Boolean('Autoretention')
    description = fields.Text()
