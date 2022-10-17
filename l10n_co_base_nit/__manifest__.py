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
    'name': 'Colombian Campos Base',
    'version': '13.0.0.0.1',
    'category': 'Hidden/Dependency',
    'description': """
Campos Base Colombia
=========================================
    """,

    'author': 'MoviTrack',
    'license': 'LGPL-3',
    'version': '12.0.0.1.0',
    'depends': ['base'],
    'data': [
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/l10n_co_res_partner.xml',
        'views/ciiu.xml',
        'security/ir.model.access.csv',
        'data/ciiu.csv',
    ],
    'images': ['images/1_partner_vat.jpeg'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
