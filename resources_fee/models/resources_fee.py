# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResourcesFee(models.Model):
    _name = "resources.fee"
    _description = 'Resource Fee'

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one(
        'res.partner', 'Customer', domain=[('customer', '=', True)])
    resources_fee_line_ids = fields.One2many('resources.fee.line', 'fee_id', string='Resource Fee Lines')
    start_date = fields.Date()
    end_date = fields.Date()
    payment_term = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannually', 'Semiannually'),
        ('annual', 'Annual')], default='monthly')
    contract_id = fields.Many2one('resources.fee.contract', 'Contract')
    payment_last = fields.Date('Payment Last')


class ResourcesFeeLine(models.Model):
    _name = "resources.fee.line"
    _description = 'Resource Fee Line'

    fee_id = fields.Many2one('resources.fee', 'Resource Fee')
    percentage = fields.Float('Percentage (%)')
    wage = fields.Float('Wage')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    job_id = fields.Many2one('hr.job', string="HR Job", copy=False)
    hour = fields.Float()


class ResourcesFeeContract(models.Model):
    _name = "resources.fee.contract"
    _description = 'Resource Fee Contract'

    name = fields.Char('Name', required=True)
    partner_id = fields.Many2one(
        'res.partner', 'Customer', domain=[('customer', '=', True)])
    start_date = fields.Date()
    end_date = fields.Date()
