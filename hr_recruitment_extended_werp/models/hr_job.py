# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class HrJob(models.Model):
    _inherit = "hr.job"

    name = fields.Char(string='Job Position', required=True, index=True, translate=False)
    default = fields.Boolean('Default?')
    hr_stage_perc_ids = fields.One2many(
        'hr.stage.perc',
        'hr_job_id',
        'Stage Percentage')
    jca_details_id = fields.Many2one('jca.details', 'JCA')
    jca_details_type = fields.Selection(related='jca_details_id.type_of_level', string='JCA Type of Level')
    macro_area_id = fields.Many2one('macro.area', 'Macro Area')
    work_group_id = fields.Many2one('work.group', 'Work Group')
    function_executed_id = fields.Many2one('function.executed', 'Function Executed')
    hour_value = fields.Float('Hour Value')
    group_id = fields.Many2one('res.groups', 'Group Reference')
    color_code = fields.Char('Color Code')

    holding = fields.Selection([
        ('AP.', 'ACCOUNT PLANNING'),
        ('AS.', 'ACCOUNT SERVICE'),
        ('AD.', 'ADMINISTRATIVE AND SECRETARIAL SUPPORT'),
        ('CR.', 'CREATIVE'),
        ('DA.', 'DATA AND ANALYTICS'),
        ('CS.', 'CREATIVE SERVICE AND DESIGN GRAPHIC'),
        ('EX.', 'EXECUTIVE'),
        ('FTEDFIacp', 'ACCOUNTING O ACCOUNTS PAYABLE'),
        ('FI.', 'FINANCE ACCOUNTING'),
        ('FTEDFIglf', 'GENERAL LEDGER / FINANCIAL REPORTING'),
        ('FTEDFIbil', 'MEDIA BILLING AND RECONCILIATION'),
        ('FTEDFIoth', 'OTHER FINANCE / ACCOUNTING'),
        ('FTEDHRhrm', 'HR MANAGEMENT'),
        ('HR.', 'HUMAN RESOURCES'),
        ('FTEDHRben', 'HUMAN RESOURCES O BENEFITS / HEALTHCARE'),
        ('FTEDHRoth', 'OTHER HUMAN RESOURCES'),
        ('FTEDHRpay', 'PAYROLL'),
        ('FTEDITass', 'ASSET AND SOFTWARE MANAGEMENT'),
        ('FTEDITbil', 'BILLABLE CLIENT IT SERVICES'),
        ('FTEDITdes', 'DESKTOP SUPPORT'),
        ('FTEDITitm', 'IT / TECHNOLOGY MANAGEMENT'),
        ('FTEDITnet', 'NETWORK / INFRASTRUCTURE'),
        ('FTEDIToth', 'OTHER IT / TECHNOLOGY'),
        ('MK.', 'MARKETING NEW BUSINESS'),
        ('OS.', 'OFFICE SERVICES'),
        ('OTH.', 'OTHER'),
        ('RE.', 'RESEARCH'),
        ('TR.', 'TRAFFIC'),
        ('FTEDFIacr', 'ACCOUNTS RECEIVABLE'),
        ('FTEDHRbil', 'BILLABLE CLIENT HR SERVICES'),
        ('MEDIA', 'MEDIA'),
        ('BP', 'Broadcast Production'),
        ('PP', 'PRINT PRODUCTION')
    ], 'Holding')
    codigo_holding = fields.Selection([
        ('AP.', 'AP.'),
        ('AS.', 'AS.'),
        ('AD.', 'AD.'),
        ('CR.', 'CR.'),
        ('DA.', 'DA.'),
        ('CS.', 'CS.'),
        ('EX.', 'EX.'),
        ('FTEDFIacp', 'FTEDFIacp'),
        ('FI.', 'FI.'),
        ('FTEDFIglf', 'FTEDFIglf'),
        ('FTEDFIbil', 'FTEDFIbil'),
        ('FTEDFIoth', 'FTEDFIoth'),
        ('FTEDHRhrm', 'FTEDHRhrm'),
        ('HR.', 'HR.'),
        ('FTEDHRben', 'FTEDHRben'),
        ('FTEDHRoth', 'FTEDHRoth'),
        ('FTEDHRpay', 'FTEDHRpay'),
        ('FTEDITass', 'FTEDITass'),
        ('FTEDITbil', 'FTEDITbil'),
        ('FTEDITdes', 'FTEDITdes'),
        ('FTEDITitm', 'FTEDITitm'),
        ('FTEDITnet', 'FTEDITnet'),
        ('FTEDIToth', 'FTEDIToth'),
        ('MK.', 'MK.'),
        ('OS.', 'OS.'),
        ('OTH.', 'OTH.'),
        ('RE.', 'RE.'),
        ('TR.', 'TR.'),
        ('FTEDFIacr', 'FTEDFIacr'),
        ('FTEDHRbil', 'FTEDHRbil'),
        ('MEDIA', 'MEDIA'),
        ('BP', 'BP'),
        ('PP', 'PP')
    ], 'Codigo Holding')
    holding_principal = fields.Selection([
        ('AP.', 'ACCOUNT PLANNING'),
        ('AS.', 'ACCOUNT SERVICE'),
        ('AD.', 'ADMINISTRATIVE AND SECRETARIAL SUPPORT'),
        ('CR.', 'CREATIVE'),
        ('DA.', 'DATA AND ANALYTICS'),
        ('CS', 'CREATIVE SERVICE AND DESIGN GRAPHIC'),
        ('EX', 'EXECUTIVE'),
        ('FI', 'FINANCE ACCOUNTING'),
        ('HR', 'HUMAN RESOURCES'),
        ('IT', 'IT / TECH'),
        ('MK.', 'MARKETING NEW BUSINESS'),
        ('OS.', 'OFFICE SERVICES'),
        ('OTH.', 'OTHER'),
        ('RE.', 'RESEARCH'),
        ('TR.', 'TRAFFIC'),
        ('MD', 'MEDIA'),
        ('BP', 'Broadcast Production'),
        ('PP', 'PRINT PRODUCTION')
    ], 'Holding Principal')
    codigo_holding_principal = fields.Selection([
        ('AP', 'AP'),
        ('AS', 'AS'),
        ('AD', 'AD'),
        ('CR', 'CR'),
        ('DA', 'DA'),
        ('CS', 'CS'),
        ('EX', 'EX'),
        ('FI', 'FI'),
        ('HR', 'HR'),
        ('IT', 'IT'),
        ('MK', 'MK'),
        ('OS', 'OS'),
        ('OTH', 'OTH'),
        ('RE', 'RE'),
        ('TR', 'TR'),
        ('MD', 'MD'),
        ('BP', 'BP'),
        ('PP', 'PP')
    ], 'Codigo Holding Principal')
    level = fields.Integer('Level')
    fte = fields.Selection([
        ('Direct', 'Direct'),
        ('Indirect', 'Indirect')
    ], string="FTE")
    active = fields.Boolean(string='Active', default=True)

    @api.multi
    def create_group(self, vals):
        valsgroup = {}
        valsgroup = {
                'name': vals.get('name'),
                }
        group_id = self.env['res.groups'].with_context({'group_create': True}).create(valsgroup)
        vals['group_id'] = group_id.id
        return vals

    @api.model
    def create(self, vals):
        if not self.env.context.get('job_create'):
            vals = self.create_group(vals)
        res = super(HrJob, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('active') is False:
            if self.no_of_employee:
                raise UserError(_("You can't inactive this Job Position because of this reference to other employees!"))
        return super(HrJob, self).write(vals)

    @api.constrains('hr_stage_perc_ids')
    def _check_state(self):
        for record in self:
            stage_names = []
            duplicate_name = ''
            for stage_per_id in record.hr_stage_perc_ids:
                stage_name = stage_per_id.stage_id.name
                if stage_name not in stage_names:
                    stage_names.append(stage_name)
                else:
                    duplicate_name += stage_name + ', '
            if duplicate_name:
                raise ValidationError(_("Please, change the stage, "
                                        "you should only have one record per "
                                        "stage (%s)!") % (duplicate_name[:-2]))

    @api.onchange('function_executed_id')
    def onchange_function_executed_id(self):
        """Select Work Group."""
        if self.function_executed_id:
            work_group_rec = [0]
            for work_group_id in self.env['work.group'].search([(
                    'function_executed_ids', '!=', False)]):
                if self.function_executed_id.id in\
                        work_group_id.function_executed_ids.ids:
                    work_group_rec.append(work_group_id.id)
            return {'domain': {'work_group_id': [
                ('id', 'in', work_group_rec)]}}
        return {'domain': {'work_group_id': [
            ('id', '=', 0)]}}

    @api.onchange('work_group_id')
    def onchange_work_group_id(self):
        """Select Macro Area."""
        if self.work_group_id:
            macro_area_rec = [0]
            for macro_area_id in self.env['macro.area'].search([(
                    'work_group_ids', '!=', False)]):
                if self.work_group_id.id in\
                        macro_area_id.work_group_ids.ids:
                    macro_area_rec.append(macro_area_id.id)
            return {'domain': {'macro_area_id': [
                ('id', 'in', macro_area_rec)]}}
        return {'domain': {'macro_area_id': [
            ('id', '=', 0)]}}
