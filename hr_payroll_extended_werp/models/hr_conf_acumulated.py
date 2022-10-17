# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrConfAcumulated(models.Model):
    """Hr Conf Acumulated."""

    _name = "hr.conf.acumulated"
    _description = "Hr Conf Acumulated"

    name = fields.Char()
    rules_add_ids = fields.One2many(
        'hr.acumulated.rules', 'hr_conf_acumulated_p_id', string='+ ')
    rules_substract_ids = fields.One2many(
        'hr.acumulated.rules', 'hr_conf_acumulated_m_id', string='- ')
    active = fields.Boolean(default=True)
