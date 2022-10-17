# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    """Added the postulant details in the partner."""

    _inherit = "res.partner"

    @api.multi
    def create_employee(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.create.employee.wizard',
            'target': 'new',
        }
