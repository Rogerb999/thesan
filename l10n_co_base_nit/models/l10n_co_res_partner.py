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

from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
import re
import logging
_logger = logging.getLogger(__name__)

class PartnerInfoExtended(models.Model):
	_inherit = 'res.partner'

	companyBrandName = fields.Char("Nombre del establecimiento")
	x_pn_retri = fields.Selection(selection =
									[
										("6", "Simplified"),
										("23", "Natural Person"),
										("7", "Common"),
										("11", "Great Taxpayer Autorretenedor"),
										("22", "International"),
										("25", "Common Autorretenedor"),
										("24", "Great Contributor")
									], 
									string="Tax Regime",
									default="6"                                    
								  )

	ciiu = fields.Many2one('ciiu', "Actividad de la CIIU")
	change_country = fields.Boolean(string="Change Country / Department?",
									default=True, store=False)
	xbirthday = fields.Date("Fecha de nacimiento")

	@api.multi
	def get_doctype(self, cr, uid, context={'lang': 'es_CO'}):
		result = []
		for item in self.pool.get('res.partner').fields_get(cr, uid, allfields=['l10n_co_document_type'], context=context)['l10n_co_document_type']['selection']:
			result.append({'id': item[0], 'name': item[1]})
		return result

	#@api.multi
	@api.onchange('firstname', 'other_name', 'lastname', 'other_lastname')
	def _concat_name(self):
		if self.firstname:
			self.firstname = self.firstname.upper()
		if self.other_name:
			self.other_name = self.other_name.upper()
		if self.lastname:
			self.lastname = self.lastname.upper()
		if self.other_lastname:
			self.other_lastname = self.self.other_lastname.upper()
		nameList = [
			self.firstname if self.firstname else '',
			self.other_name if self.other_name else '',
			self.lastname if self.lastname else '',
			self.other_lastname if self.other_lastname else ''
		]

	#@api.one
	@api.onchange('change_country')
	def on_change_address(self):
		if self.change_country is True:
			self.country_id = False
			self.state_id = False
			self.city_id = False

	@api.multi
	def _check_dv(self, nit):
		for item in self:
			if item.l10n_co_document_type != "rut" and item.nit:
				return str(nit)

			nitString = '0'*(15-len(nit)) + nit
			vl = list(nitString)
			result = (
							 int(vl[0])*71 + int(vl[1])*67 + int(vl[2])*59 + int(vl[3])*53 +
							 int(vl[4])*47 + int(vl[5])*43 + int(vl[6])*41 + int(vl[7])*37 +
							 int(vl[8])*29 + int(vl[9])*23 + int(vl[10])*19 + int(vl[11])*17 +
							 int(vl[12])*13 + int(vl[13])*7 + int(vl[14])*3
					 ) % 11

			if result in (0, 1):
				return str(result)
			else:
				return str(11-result)

	# @api.multi
	def onchange_location(self, cr, uid, ids, country_id=False,
						  state_id=False):
		if country_id:
			mymodel = 'res.country.state'
			filter_column = 'country_id'
			check_value = country_id
			domain = 'state_id'

		elif state_id:
			mymodel = 'res.country.state.city'
			filter_column = 'state_id'
			check_value = state_id
			domain = 'city_id'
		else:
			return {}

		obj = self.pool.get(mymodel)
		ids = obj.search(cr, uid, [(filter_column, '=', check_value)])
		return {
			'domain': {domain: [('id', 'in', ids)]},
			'value': {domain: ''}
		}

	#@api.multi
	@api.constrains('vat_num')
	def _check_ident(self):
		partner_ids = self.env['res.partner'].search([('vat_num', '=', '')])
		data = []
		if partner_ids:
			for x in partner_ids:
				data.append(x.id)
		_logger.info(data)
		for item in self:
			if not item.l10n_co_document_type:
				msg = _('¡Error! El número de dígitos del número de identificación debe ser entre 2 y 12')
				
				_logger.info(item.id)
				_logger.info(item.name)
				_logger.info((str(item.vat_num)))
				_logger.info(len(str(item.vat_num)))
				if len(str(item.vat_num)) < 2:
					raise exceptions.ValidationError(msg)
				elif len(str(item.vat_num)) > 14:
					raise exceptions.ValidationError(msg)

	#@api.multi
	@api.constrains('vat_num')
	def _check_ident_num(self):
		for item in self:
			if item.l10n_co_document_type:
				if item.vat_num and \
						item.l10n_co_document_type != "foreign_id_card" and \
						item.l10n_co_document_type != "passport":
					if re.match("^[0-9]+$", item.vat_num) is None:
						msg = _('¡Error! El número de identificación solo puede tener números')
						raise exceptions.ValidationError(msg)

	#@api.one
	@api.constrains('l10n_co_document_type')
	def _checkDocType(self):
		if self.l10n_co_document_type :
			if not self.l10n_co_document_type:
				msg = _('¡Error! Elija un tipo de identificación')
				raise exceptions.ValidationError(msg)

	#@api.one
	def _display_address(self, without_company=False):
		address_format = self._get_address_format()
		args = {
			'state_code': self.state_id.code or '',
			'state_name': self.state_id.name or '',
			'country_code': self.country_id.code or '',
			'country_name': self._get_country_name(),
			'company_name': self.commercial_company_name or '',
		}
		for field in self._formatting_address_fields():
			args[field] = getattr(self, field) or ''
		if without_company:
			args['company_name'] = ''
		elif self.commercial_company_name:
			address_format = '%(company_name)s\n' + address_format

		args['city'] = args['city'].capitalize() + ','
		return address_format % args
