from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_no_need_to_bill = fields.Boolean(string="No obligado a Facturar?", default=False)
    