# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AnimalRace(models.Model):
    """This Class is used to define fields and methods for Animal Race."""

    _name = "animal.race"
    _description = "Animal Race"

    name = fields.Char('Name')
    animal_type_id = fields.Many2one('animal.type', 'Animal Type')
    description = fields.Text('Description')
