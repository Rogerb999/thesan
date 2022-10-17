# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrAcumulatedRules(models.Model):
    """Hr Acumulated Rules."""

    _name = "hr.acumulated.rules"
    _description = "Hr Acumulated Rules"
    _rec_name = "rule_id"

    @api.model
    def create(self, vals):
        if not vals.get('sign', ''):
            if vals.get('hr_conf_acumulated_p_id'):
                vals['sign'] = 'plus'
            if vals.get('hr_conf_acumulated_m_id'):
                vals['sign'] = 'minus'
        if vals.get('sign', ''):
            if vals.get('hr_conf_acumulated_p_id') and vals['sign'] == 'minus':
                vals['sign'] = 'plus'
            if vals.get('hr_conf_acumulated_m_id') and vals['sign'] == 'plus':
                vals['sign'] = 'minus'
        return super(HrAcumulatedRules, self).create(vals)

    sign = fields.Selection(
        [('plus', '+'),
         ('minus', '-')])
    rule_id = fields.Many2one(
        'hr.salary.rule', 'Salary Rule',
        domain=[('accumulate', '=', True)]
    )
    hr_conf_acumulated_p_id = fields.Many2one('hr.conf.acumulated')
    hr_conf_acumulated_m_id = fields.Many2one('hr.conf.acumulated')
