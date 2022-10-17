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
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat_type = fields.Selection([
        ('11', u'11 - Registro Civil'),
        ('12', u'12 - Tarjeta de identidad'),
        ('13', u'13 - Cédula de ciudadanía'),
        ('21', u'21 - Tarjeta de extranjería'),
        ('22', u'22 - Cédula de extranjería'),
        ('31', u'31 - NIT (Número de identificación tributaria)'),
        ('41', u'41 - Pasaporte'),
        ('42', u'42 - Documento de identificación extranjero'),
        ('43', u'43 - Sin identificación del exterior o para uso definido por la DIAN')
    ], string='VAT type',
        help='''Customer identifier, according to types given by the DIAN.
                If it is a natural person and has RUT use NIT''',
        required=False
    )
    vat_vd = fields.Char('vd', size=1, help='Digito de verificación', store=True)
    firstname = fields.Char()
    other_name = fields.Char()
    lastname = fields.Char()
    other_lastname = fields.Char()
    name = fields.Char(index=True)
    vat_num = fields.Char(string='NIF')

    #@api.multi
    @api.onchange('firstname', 'other_name', 'lastname', 'other_lastname')
    def _name_compute(self):
        for rec in self:
            if rec.company_type == 'person':
                rec.name = (str(rec.firstname) if rec.firstname else '') \
                           + ' ' + (str(rec.other_name) if rec.other_name else '') \
                           + ' ' + (str(rec.lastname) if rec.lastname else '') \
                           + ' ' + (str(rec.other_lastname) if rec.other_lastname else '')

    #@api.one
    @api.onchange('vat_num')
    def _on_chage_vat(self):
        if self.l10n_co_document_type == 'rut':
            self.vat = str(self.vat_num) + '-' + str(self.vat_vd)
            self.vat_vd = self._check_vat_co()
        else:
            self.vat = self.vat_num

    #@api.one
    @api.onchange('vat_vd')
    def _on_chage_vat_dv(self):
        if self.l10n_co_document_type == 'rut':
            self.vat = str(self.vat_num) + '-' + str(self.vat_vd)
        else:
            self.vat = self.vat_num

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for record in self:
            if record.child_ids:
                for child in record.child_ids:
                    vals_ch= {
                        'vat_num' : record.vat_num,
                        'vat_vd' : record.vat_vd,
                        'vat' : record.vat,
                        'l10n_co_document_type' : record.l10n_co_document_type,
                        'vat_type' : record.vat_type,
                    }
                    child.write(vals_ch)
        return res

    @api.one
    @api.depends('vat_type', 'vat_num')
    def _check_vat_co(self):
        if self.vat_type != '31':
            return ''
        factor = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        factor = factor[-len(self.vat_num):]
        csum = sum([int(self.vat_num[i]) * factor[i] for i in range(len(self.vat_num))])
        check = csum % 11
        if check > 1:
            check = 11 - check
        return check

    def _onerror_msg(self, msg):
        return {'warning': {'title': _('Error!'), 'message': _(msg)}}

    #@api.one
    @api.onchange('vat_type')
    def onchange_vat_type(self):

        return {'value': {'is_company': self.vat_type == '31'}}

    def _commercial_fields(self):
        return ['website']

    def copy(self):
        [partner_dic] = self.read(['name', 'vat', 'vat_num', 'vat_vd'])
        default = {}
        default.update({
            'name': '(copy) ' + partner_dic.get('name'),
        })
        return super(ResPartner, self).copy(default)

    def _check_vat(self):
        if self.company_id and self.vat and self.search(
                [('company_id', '=', self.company_id.id), ('vat', '=ilike', self.vat),
                 ('parent_id', '=', None)]).id != self.id:
            return False
        return True

    #@api.one
    @api.onchange("l10n_co_document_type")
    def onchange_document_type(self):
        if self.l10n_co_document_type == 'rut':
            self.vat_type = '31'
        elif self.l10n_co_document_type == 'id_document':
            self.vat_type = '13'
        elif self.l10n_co_document_type == 'id_card':
            self.vat_type = '12'
        elif self.l10n_co_document_type == 'passport':
            self.vat_type = '41'
        elif self.l10n_co_document_type == 'foreign_id_card':
            self.vat_type = '22'
        elif self.l10n_co_document_type == 'external_id':
            self.vat_type = '42'
        elif self.l10n_co_document_type == 'diplomatic_card':
            self.vat_type = '42'
        elif self.l10n_co_document_type == 'residence_document':
            self.vat_type = '42'
        elif self.l10n_co_document_type == 'civil_registration':
            self.vat_type = '11'
        elif self.l10n_co_document_type == 'national_citizen_id':
            self.vat_type = '13'

