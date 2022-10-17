# -*- coding: utf-8 -*-
##############################################################################
#
#    MoviTrack
#    Copyright (C) 2020-TODAY MoviTrack.
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api

class IndustrialClassification(models.Model):
    _name = "ciiu"  # res.co.ciiu
    _description = "ISIC List"

    name = fields.Char(
        string="Code and Description",
        store=True,
        compute="_compute_concat_name"
    )
    code = fields.Char('Code', required=True)
    description = fields.Char('Description', required=True)
    type = fields.Char(
        'Type',
        store=True,
        compute="_compute_set_type"
    )
    has_parent = fields.Boolean('Has Parent?')
    parent = fields.Many2one('ciiu', 'Parent')

    has_division = fields.Boolean('Has Division?')
    division = fields.Many2one('ciiu', 'Division')

    has_section = fields.Boolean('Has Section?')
    section = fields.Many2one('ciiu', 'Section')

    hierarchy = fields.Selection(
        [
            ("1", 'Has Parent?'),
            ("2", 'Has Division?'),
            ("3", 'Has Section?')
        ],
        'Hierarchy'
    )

    @api.multi
    @api.depends('code', 'description')
    def _compute_concat_name(self):
        for rec in self:
            if rec.code is False or rec.description is False:
                rec.name = ''
            else:
                rec.name = str(rec.code.encode('utf-8').strip()) + \
                    ' - ' + str(rec.description.encode('utf-8').strip())

    @api.multi                    
    @api.depends('has_parent')
    def _compute_set_type(self):
        for rec in self:
            # Child
            if rec.has_parent is True:
                if rec.division is True:
                    rec.type = 'view'
                elif rec.section is True:
                    rec.type = 'view'
                else:
                    rec.type = 'other'
            # Division
            else:
                rec.type = 'view'
