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
    'name': "Magentic Media",
    'summary': """
        Magnetic Media report.""",
    'author': 'MoviTrack',
    'category': 'Account',
    "version": "12.0.1.0.0",
    'depends': ['account','l10n_co_location','l10n_co_base_nit'],
    'data': [
        'security/ir.model.access.csv',
        'data/1001.xml',
        'data/1003.xml',
        'data/1004.xml',
        'data/1005.xml',
        'data/1006.xml',
        'data/1007.xml',
        'data/1008.xml',
        'data/1009.xml',
        'data/1010.xml',
        'data/1011.xml',
        'data/1012.xml',
        'data/2276.xml',
        'data/art_2.xml',
        'data/art_4.xml',
        'data/art_6.xml',
        'data/account.account.tag.csv',
        'data/magnetic.media.lines.csv',
        'data/magnetic.media.lines.concepts.csv',
        'views/magnetic_media_views.xml',
        'views/res_country_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
