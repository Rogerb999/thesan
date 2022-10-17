# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrCvEmployee(models.Model):
    """Hr Cv Employee."""

    _inherit = "hr.cv.employee"

    partner_id = fields.Many2one('res.partner', 'Contact')

    @api.constrains('partner_id')
    def _check_company_payment(self):
        if self.search_count([('partner_id', '=', self.partner_id.id)]) > 1:
            raise ValidationError(_(
                "Contact Already Exist in the another record."))
