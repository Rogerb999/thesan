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


class CountryStateCity(models.Model):
    _name = 'res.country.state.city'
    _description = 'Cities of states'

    state_id = fields.Many2one('res.country.state', string='State', required=True)
    name = fields.Char(required=True)
    code = fields.Char(string='City code', required=True)
    country_id = fields.Many2one('res.country', 'Country')

class ResState(models.Model):
    _inherit = 'res.country.state'

    dian_state_code = fields.Char(string='Código de estado')

class Partner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one('res.country.state.city', string='City Ref', ondelete='restrict', required=False)

    @api.multi
    @api.onchange('city_id')
    def onchange_city(self):
        return {'value': {'state_id': self.city_id.state_id.id,
                          'city': self.city_id.name,
                          'country_id': self.city_id.state_id.country_id.id}}


class Bank(models.Model):
    _inherit = 'res.bank'

    city_id = fields.Many2one('res.country.state.city', string='City Ref', ondelete='restrict')

    @api.multi
    @api.onchange('city_id')
    def onchange_city(self):
        return {'value': {'state': self.city_id.state_id.id,
                          'city': self.city_id.name,
                          'country_id': self.city_id.state_id.country_id.id}}


class Company(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one('res.country.state.city', string='City Ref', ondelete='restrict')

    @api.multi
    @api.onchange('city_id')
    def onchange_city(self):
        return {'value': {'state_id': self.city_id.state_id.id,
                          'city': self.city_id.name,
                          'country_id': self.city_id.state_id.country_id.id}}
