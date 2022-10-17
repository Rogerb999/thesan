# -*- coding: utf-8 -*-

from odoo import api, fields, models


class NoveltyCreateContact(models.TransientModel):
    _name = 'novelty.create.contact'
    _description = 'Novelty Create Contact'

    first_name = fields.Char()
    second_name = fields.Char()
    surname = fields.Char()
    second_surname = fields.Char()
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    city_id = fields.Many2one('res.city', 'City')
    state_id = fields.Many2one(
        'res.country.state', 'State',
        domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', 'Country')
    l10n_co_document_type = fields.Selection(
        [('rut', 'NIT'),
         ('id_document', 'Cédula'),
         ('id_card', 'Tarjeta de Identidad'),
         ('passport', 'Pasaporte'),
         ('foreign_id_card', 'Cédula Extranjera'),
         ('external_id', 'ID del Exterior'),
         ('diplomatic_card', 'Carné Diplomatico'),
         ('residence_document', 'Salvoconducto de Permanencia'),
         ('civil_registration', 'Registro Civil'),
         ('national_citizen_id', 'Cédula de ciudadanía'),
         ('NIT', 'N.I.T.'),
         ('external_NIT', 'Nit Extranjería'),
         ('external_society_without_NIT',
          'Sociedad extranjera sin N.I.T. En Colombia'),
         ('trust', 'Fideicomiso'),
         ('natural_person_NIT', 'Nit persona natural')],
        string="Document Type")
    vat = fields.Char('Document Number')

    @api.multi
    def confirm(self):
        """Create Partner."""
        active_id = self.env.context.get('active_id')
        partner = self.env['res.partner'].create({
            'name': self.first_name,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'surname': self.surname,
            'second_surname': self.second_surname,
            'gender': self.gender,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'city_id': self.city_id.id,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'l10n_co_document_type': self.l10n_co_document_type,
            'vat': self.vat,
            'postulant': True,
        })
        partner.onchange_name()
        novelty_id = self.env['hr.novelty'].browse(active_id)
        novelty_id.write({
            'contact_id': partner.id})
