# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PartnerStateSelectionWizard(models.TransientModel):
    """Partner State Selection Wizard."""

    _name = 'partner.state.selection.wizard'
    _description = "Partner State Selection Wizard"

    state_selection = fields.Selection([
        ('eligible', 'Eligible'),
        ('not_elig0ible', 'Not Eligible'),
        ('in_process', 'In Process'),
        ('hired', 'Hired'),
    ], string='Contact State Selection', required=1)

    @api.multi
    def action_select_state(self):
        """Select state of the partner."""
        for partner in self:
            context = self._context
            if context.get('active_model', '') and context.get(
                    'active_id', ''):
                applicant = self.env[context.get('active_model', '')].browse(
                    context.get('active_id', ''))
                applicant.partner_id.state_selection = partner.state_selection
                applicant.write({'active': False})
