# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class HrContract(models.Model):
    """Hr Contract."""

    _inherit = "hr.contract"

    @api.model
    def create(self, vals):
        """Fill employee based on the identification."""
        res = super(HrContract, self).create(vals)
        if res.identification_id_fill and not res.employee_id:
            partner_rec_rec = self.env['res.partner'].search(
                [('vat', '=', res.identification_id_fill)], limit=1)
            if partner_rec_rec:
                employee_rec = self.env['hr.employee'].search(
                    [('address_home_id', '=', partner_rec_rec.id)],
                    limit=1)
                if employee_rec:
                    res.employee_id = employee_rec.id
                    res._onchange_employee_id()
        return res

    @api.depends('employee_id.address_home_id.vat')
    def _compute_identification_id(self):
        for rec in self:
            if rec.employee_id.address_home_id.vat:
                rec.identification_id = rec.employee_id.address_home_id.vat

    leave_generate_id = fields.Many2one(
        'hr.leaves.generate', 'Leave Generate')
    identification_id = fields.Char(
        compute='_compute_identification_id', string='Identification No',
        store=True)
    identification_id_fill = fields.Char('Identification No Fill')
