# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ContactReference(models.Model):
    _name = 'contact.reference'
    _description = 'Contact Reference'
    _rec_name = 'contact'

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        domain=[('customer', '=', True), ('supplier', '=', True)])
    contact = fields.Char('Contact', required=True)
    relation = fields.Selection([
        ('shareholder', 'Shareholder'),
        ('friend', 'Friend'),
        ('contractor', 'Contractor'),
        ('wife', 'Wife'),
        ('sister', 'Sister'),
        ('daughter', 'Daughter'),
        ('bride', 'Bride'),
        ('premium', 'Premium'),
        ('aunt', 'Aunt'),
        ('others', 'Others'),
    ])
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
