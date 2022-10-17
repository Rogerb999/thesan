# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import odoo
import logging
from odoo import http
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    """Extend Partner."""

    _inherit = 'res.partner'

    is_found_layoffs = fields.Boolean(string='Found Layoffs')
    is_compensation_box = fields.Boolean(string='Compensation Box')
    is_eps = fields.Boolean(string='EPS')
    is_unemployee_fund = fields.Boolean(string='Unemployee Fund')
    is_arl = fields.Boolean(string='ARL')
    is_prepaid_medicine = fields.Boolean(string='Prepaid Medicine')
    is_afc = fields.Boolean(string='AFS')
    is_voluntary_contribution = fields.Boolean(string='Voluntary Contribution')
    is_afp = fields.Boolean(string='AFP')
    file_cv = fields.Binary(string='File', attachment=True)
    attachment_url = fields.Char("URL")
    file_cv_name = fields.Char(string='File CV Name')
    file_cv_size = fields.Char(string='File CV Size')
    mobile_country_code = fields.Char(string='Mobile Country Code')
    phone_country_code = fields.Char(string='Phone Country Code')
    l10n_co_document_type = fields.Selection(
        selection_add=[
            ('NIT', 'N.I.T.'),
            ('external_NIT', 'Nit Extranjería'),
            ('external_society_without_NIT',
             'Sociedad extranjera sin N.I.T. En Colombia'),
            ('trust', 'Fideicomiso'),
            ('natural_person_NIT', 'Nit persona natural')])
    function_id = fields.Many2one('hr.job', 'Job Position')
    client_reference = fields.Integer('Client Reference')


class ResUsers(models.Model):
    """Extend Users."""

    _inherit = "res.users"

    birthdate = fields.Date('Date of birth')
