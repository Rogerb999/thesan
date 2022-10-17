# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrPayrollInterface(models.Model):
    """Hr Payroll Interface."""

    _name = 'hr.payroll.interface'
    _description = 'Hr Payroll Interface'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(track_visibility='always')
    hr_type_interface_id = fields.Many2one(
        'hr.type.interface', track_visibility='always')
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')],
                             default='draft',
                             track_visibility='onchange')
    start_date = fields.Date('Start Date', track_visibility='always')
    end_date = fields.Date('End Date', track_visibility='always')
    payslip_ids = fields.Many2many('hr.payslip')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        """Override the method to add sequence number."""
        seq = self.env['ir.sequence'].next_by_code(
            'hr.payroll.interface')
        if seq:
            vals.update({'name': seq})
        return super(HrPayrollInterface, self).create(vals)

    @api.onchange('start_date', 'end_date')
    def onchange_date(self):
        """Added domain to select Payslip."""
        if self.start_date and self.end_date:
            return {'domain': {'payslip_ids': [
                ('state', '=', 'done'),
                ('date_from', '>=', self.start_date),
                ('date_to', '<=', self.end_date)]}}
        else:
            return {'domain': {'payslip_ids': [('id', '=', 0)]}}

    @api.multi
    def action_done(self):
        """Move in Done state."""
        for rec in self:
            rec.state = 'done'

    @api.multi
    def action_cancel(self):
        """Move in Cancel state."""
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def action_draft(self):
        """Move in Draft state."""
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def send_mail_from_draft_done(self):
        """Code for draft and done state mail send."""
        for rec in self:
            email_template_share = self.env.ref(
                'hr_payroll_interface.email_template_concepts_period')
            if rec.env.context.get('draft_button'):
                partner_ids = rec.hr_type_interface_id.from_draft_ids
            elif rec.env.context.get('done_button'):
                partner_ids = rec.hr_type_interface_id.from_done_ids
            if partner_ids:
                format_ids = rec.hr_type_interface_id.formats_ids
                if not format_ids:
                    email_template_share.send_mail(
                        self.id, force_send=True,
                        email_values={'recipient_ids': [
                            (6, 0, partner_ids.ids)]})
                else:
                    for format_temp in format_ids:
                        report_name = ''
                        if format_temp.name == \
                                'CMT - SUMMARY BY CONCEPTS - PERIOD':
                            report_name = 'ACUMULADO '
                        if format_temp.name == \
                                'GENERATION PAYMENT':
                            report_name = 'GENERATION PAYMENT '
                        report_name += rec.company_id.name + ' ' + \
                            rec.create_date.strftime('%B') + \
                            ' ' + rec.create_date.strftime('%Y')
                        email_template_share.write(
                            {'report_template': format_temp.id,
                             'report_name': report_name})
                        email_template_share.send_mail(
                            self.id, force_send=True, email_values={
                                'recipient_ids': [
                                    (6, 0,
                                     partner_ids.ids)]
                            })
                        email_template_share.write(
                            {'report_template': None, 'report_name': None})
