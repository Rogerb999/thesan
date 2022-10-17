from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    month = fields.Integer(string='Months')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['month'] = int(self.env['ir.config_parameter'].sudo().get_param(
            'month', default=6))
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('month', self.month)
        super(ResConfigSettings, self).set_values()
