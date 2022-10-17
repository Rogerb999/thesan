# -*- coding: utf-8 +-*

from odoo import models, fields


class HrLeave(models.Model):
    _inherit = 'hr.leave'
    
    non_attendance_leave = fields.Boolean(string='Ausencia automaática')
    non_attendance_date = fields.Date(string='Fecha de ausencia')


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    leave_type = fields.Selection([('incapacidad_arl', 'Incapacidad Laboral ARL'),
                                   ('incapacidad_eps', 'Incapacidad Enfermedad EPS'),
                                   ('vacaciones', 'Vacaciones'),
                                   ('otro', 'Otro')], string='Tipo ausencia (Nomina)')
