# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging
from odoo.exceptions import Warning
from datetime import timedelta
_logger = logging.getLogger(__name__)


class HrContractBatch(models.Model):
    _name = 'hr.contract.batch'
    _inherit = 'mail.thread'
    _description = 'Contract Batch Processing'

    name = fields.Char(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    wage_field = fields.Selection([
        ('wage', 'Wage'),
        ('fix', 'Fix Wage'),
        ('flex', 'Flex Wage'),
        ('both', 'Both')
    ], track_visibility='onchange')
    contract_ids = fields.Many2many('hr.contract', string='Contracts', copy=False)
    new_contract_ids = fields.Many2many('hr.contract', 'hr_contract_new_batch_rel',
                                        'contract_id', 'batch_id', string='New Contracts', copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In-Progress'),
                              ('done', 'Done')], default='draft', track_visibility='onchange')
    type_assignment = fields.Selection(
        [('value', 'Value'), ('percentage', 'Percentage')]
    )
    percentage = fields.Float('Percentage')
    amount_fix = fields.Float('Amount Fix')
    amount_flex = fields.Float('Amount Flex')

    @api.constrains('wage_field', 'type_assignment')
    def _check_wage_field_type_assignment(self):
        if self.wage_field == 'both' and self.type_assignment != 'value':
            raise Warning(_("You can select Wage Field as 'Both' only when Type Assignment is Value!"))

    @api.multi
    def action_in_process(self):
        self.state = 'in_progress'

    @api.multi
    def action_create_batch_contract(self):
        new_contract_ids = []
        for contract in self.contract_ids:
            new_contract_ids.append(self.batch_process(contract, self.wage_field))
        self.write({
            'state': 'done',
            'new_contract_ids': [(6, 0, new_contract_ids)]
        })

    @api.multi
    def set_flex(self, new_contract, hr_salary_rule_id, flex_wage_amount, amount_flex):
        flex_wage_ids = []
        old_flex_wage_amount = 0
        if new_contract.flex_wage_ids:
            if amount_flex:
                divide_amount = amount_flex / len(new_contract.flex_wage_ids)
            for fw_id in new_contract.flex_wage_ids:
                old_flex_wage_amount += fw_id.amount
                add_amount = fw_id.amount + divide_amount
                flex_wage_ids.append((0, 0,
                    {

                        'salary_rule_id': fw_id.salary_rule_id.id,
                        'fixed': fw_id.fixed,
                        'amount': add_amount,
                        'percentage': round((add_amount / flex_wage_amount) * 100,2),
                    }
                ))
        else:
            flex_wage_ids.append((0, 0,
                {
                'salary_rule_id': hr_salary_rule_id.id,
                'amount': amount_flex,
                'percentage': 100,
                'contract_id': new_contract.id,
            }))
        new_contract.write({
            'wage': new_contract.wage - old_flex_wage_amount,
            'flex_wage_ids': [(6,0,[])],
        })
        return flex_wage_ids


    @api.multi
    def batch_process(self, contract, field):
        new_contract = contract.copy()
        contract_flex_wage_obj = self.env['hr.contract.flex_wage']
        contract.write({'date_end': self.date, 'state': 'close'})
        start_date = self.date + timedelta(days=1)
        new_contract.write({'date_end': False})
        divide_amount = 0
        hr_salary_rule_id = self.env['hr.salary.rule'].search([('autocomplete_flex', '=', True)], limit=1)

        if self.wage_field == 'fix' and self.type_assignment == 'value' and + self.amount_fix:
            wage = new_contract.wage + self.amount_fix
            fix_wage_amount = new_contract.fix_wage_amount + self.amount_fix
            new_contract.write({
                'wage': wage,
                'fix_wage_amount': fix_wage_amount,
                'date_start': start_date
            })
        elif self.wage_field == 'flex' and self.type_assignment == 'value' and self.amount_flex:
            wage = new_contract.wage + self.amount_flex
            flex_wage_amount = new_contract.flex_wage_amount + self.amount_flex
            flex_wage_ids = self.set_flex(new_contract, hr_salary_rule_id, flex_wage_amount, self.amount_flex)
            vals = {
                'wage': wage,
                'flex_wage_amount': flex_wage_amount,
                'flex_wage_ids': flex_wage_ids,
                'date_start': start_date
            }
            new_contract.write(vals)

        elif self.wage_field == 'both' and self.type_assignment == 'value':
            sum_amount = self.amount_flex + self.amount_fix
            wage = new_contract.wage + sum_amount
            fix_wage_amount = new_contract.fix_wage_amount + self.amount_fix
            flex_wage_amount = new_contract.flex_wage_amount + self.amount_flex
            flex_wage_ids = self.set_flex(new_contract, hr_salary_rule_id, flex_wage_amount, self.amount_flex)
            vals = {
                'wage': wage,
                'fix_wage_amount': fix_wage_amount,
                'flex_wage_amount': flex_wage_amount,
                'flex_wage_ids': flex_wage_ids,
                'date_start': start_date
            }
            new_contract.write(vals)
        elif self.wage_field == 'fix' and self.type_assignment == 'percentage':
            per = self.percentage / 100
            wage = new_contract.wage + (new_contract.wage * per)
            fix_wage_amount = new_contract.fix_wage_amount + (new_contract.wage * per)
            new_contract.write({
                'wage': wage,
                'fix_wage_amount': fix_wage_amount,
                'date_start': start_date,
            })
        elif self.wage_field == 'flex' and self.type_assignment == 'percentage':
            per = self.percentage / 100
            flex_wage_amount_per = (new_contract.wage * per)
            wage = new_contract.wage + flex_wage_amount_per
            flex_wage_amount = new_contract.flex_wage_amount + flex_wage_amount_per
            flex_wage_ids = self.set_flex(new_contract, hr_salary_rule_id, flex_wage_amount, flex_wage_amount_per)
            vals = {
                'wage': wage,
                'flex_wage_amount': flex_wage_amount,
                'flex_wage_ids': flex_wage_ids,
                'date_start': start_date
            }
            new_contract.write(vals)
        elif self.type_assignment == 'percentage':
            per = self.percentage / 100
            flex_wage_amount_inc = new_contract.flex_wage_amount * per
            wage = new_contract.wage + (new_contract.wage * per)
            fix_wage_amount = new_contract.fix_wage_amount + (new_contract.fix_wage_amount * per)
            flex_wage_amount = new_contract.flex_wage_amount + flex_wage_amount_inc
            flex_wage_ids = self.set_flex(new_contract, hr_salary_rule_id, flex_wage_amount, flex_wage_amount_inc)
            vals = {
                'wage': wage,
                'flex_wage_amount': flex_wage_amount,
                'flex_wage_ids': flex_wage_ids,
                'fix_wage_amount': fix_wage_amount,
                'date_start': start_date
            }
            new_contract.write(vals)
        return new_contract.id
        new_contract.write({
            'date_start': start_date,
        
        })
        if field == 'wage':
            contract.wage += amount
        
        elif field == 'fix':
            contract.write({
                'fix_wage_amount': contract.fix_wage_amount + amount,
                'wage': contract.wage + amount,
            })
            # ToDo: Write message in notification chatter
        elif field == 'flex':
        
            flex_ids = contract.flex_wage_ids.filtered(
                                            lambda rec: rec.fixed is not True)
        
            subtotal = self.amount / len(flex_ids)
        
            for flex in flex_ids:
                flex.amount += subtotal
            # ToDo: use Write() to avoid constrain error
        
            contract.write({
                'wage': contract.wage + amount,
                # 'flex_wage_ids': [()]
            })
