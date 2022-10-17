# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import osv
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp

# Agrega campos EPS y Fondo de Pensiones en datos del empleado.

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    eps_id = fields.Many2one('res.partner', 'EPS')
    fp_id = fields.Many2one('res.partner', 'Fondo de Pensiones')
    fc_id =fields.Many2one('res.partner', 'Fondo de Cesantías')
    caja_compensacion_id =fields.Many2one('res.partner', 'Caja de Compensación')
    # total_cesantias = fields.Float(string='Total Cesantias', default=0.00)
