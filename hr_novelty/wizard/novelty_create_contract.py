# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class NoveltyCreateContract(models.TransientModel):
    _name = 'novelty.create.contract'
    _description = 'Novelty Create Contract'

    @api.model
    def default_get(self, lst_fields):
        """Add wage_assign and Fix_wage_assing."""
        result = super(NoveltyCreateContract, self).default_get(lst_fields)
        active_id = self.env.context.get('active_id')
        novelty_id = self.env['hr.novelty'].browse(active_id)
        if novelty_id.wage_assign:
            result['wage_assign'] = novelty_id.wage_assign
        if novelty_id.Fix_wage_assing:
            result['Fix_wage_assing'] = novelty_id.Fix_wage_assing
        struct_id = self.env['hr.payroll.structure'].search([
            ('type_id.name', '=', 'Nuevo Flex')], limit=1)
        if struct_id:
            result['struct_id'] = struct_id.id
        return result

    struct_id = fields.Many2one('hr.payroll.structure', 'Salary Structures')
    wage_assign = fields.Float()
    Fix_wage_assing = fields.Float()

    @api.constrains('wage_assign', 'Fix_wage_assing')
    def _check_wage(self):
        if self.wage_assign <= 0.0:
            raise ValidationError(_('Wage Assign should be positive.'))
        if self.Fix_wage_assing <= 0.0:
            raise ValidationError(_('Fix Wage Assign should be positive.'))

    @api.multi
    def confirm(self):
        """Create Contract."""
        active_id = self.env.context.get('active_id')
        novelty_id = self.env['hr.novelty'].browse(active_id)
        if self.struct_id and self.wage_assign and self.Fix_wage_assing and\
           novelty_id.employee_id:
            contract = self.env['hr.contract'].with_context(
                from_novelty=True).create({
                    'name': novelty_id.employee_id.name + ' Contract',
                    'employee_id': novelty_id.employee_id.id,
                    'date_start': fields.Date.today(),
                    'wage': self.wage_assign,
                    'fix_wage_amount': self.Fix_wage_assing,
                    'struct_id': self.struct_id.id,
                    'recruitment_reason_id':
                    novelty_id.recruitment_reason_id.id})
            # struct_id = self.env['hr.payroll.structure'].search([
            #     ('type_id.name', '=', 'Nuevo Flex')], limit=1)
            # if struct_id:
            # contract.write({'struct_id': struct_id.id})
            contract.onchange_struct_id()
            contract.onchange_fix_wage_amount()
            contract._onchange_employee_id()
            novelty_id.write({
                'contract_id': contract.id})
