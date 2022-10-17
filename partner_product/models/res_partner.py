# -*- coding: utf-8 -*-

from lxml import etree
import json

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    type = fields.Selection([
        ('savings', 'Savings'),
        ('current', 'Current')], "Acc Type")
    description = fields.Text()


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    agency = fields.Boolean('Agency?')
    company = fields.Boolean('Company?')
    agency_type = fields.Selection([
        ('production', 'Production'),
        ('media', 'Media'),
        ('creative', 'Creativity'),
        ('financial', 'Financial'),
        ('automotive', 'Automotive'),
        ('real_state', 'Real State'),
        ('client', 'Client'),
        ('other', 'Other'),
    ], 'Agency Type')
    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """Display city_id field."""
        ret_val = super(ResPartner, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        doc = etree.XML(ret_val['arch'])
        if view_type == 'form':
            for field in ['city_id']:
                for node in doc.xpath("//field[@name='%s']" % field):
                    node.set("modifiers", '{"attrs": {}}')
            for field in ['city']:
                for node in doc.xpath("//field[@name='%s']" % field):
                    node.set("modifiers", '{"invisible": true}')
        ret_val['arch'] = etree.tostring(doc)
        return ret_val

    @api.multi
    def link_to_employee(self):
        """Link Partner in Employee Model."""
        for rec in self:
            if rec.display_name:
                employee_rec = self.env['hr.employee'].search([
                    ('name', '=', rec.display_name),
                    ('address_home_id', '=', False)], limit=1)
                if employee_rec:
                    employee_rec.write({'address_home_id': rec.id})
