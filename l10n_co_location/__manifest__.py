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
{
    'name': "l10n_co_location",

    'summary': "Colombian info",

    'description': """
Este módulo carga:
- información geográfica de colombia (estados y ciudades).
Además, carga el código para cada ciudad y estado generado por el DANE.
- Bancos colombianos

""",
    'author': 'MoviTrack',
    'license': 'LGPL-3',
    'support': 'dev@movitrack.co',
    'category': 'res_partner',
    'version': '12.0.0.1.0',
    'depends': ['base', 'contacts'],
    'data': [
        # 'data/res.bank.csv',
        'data/res.country.state.csv',
        # 'data/res.country.state.city.csv',
        'data/res_country_state_city_data.xml',
        'security/ir.model.access.csv',
        'views/partner_city_view.xml',
        #'views/bank_city_view.xml',
        'views/res_country_state_city_view.xml',
        'views/company_city_view.xml',
        'views/res_country_state.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
