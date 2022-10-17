# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job' 
    
    riesgos_profesionales = fields.Many2one('hr.nivel.riesgos',string='Nivel Riesgos Laborales')       


class HrNivelRiesgo(models.Model):
    _name = 'hr.nivel.riesgos' 

    name = fields.Char(string='Nivel de Riesgo')
    tarifa = fields.Float(string='Tarifa', digits=(3,4)) 
