# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class MotivoTalento(models.Model):
    """Add the information of the Motivo Talento."""

    _name = "motivo.talento"
    _description = "Motivo Talento"

    name = fields.Char()
