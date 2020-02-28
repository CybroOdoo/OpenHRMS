# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Yadhu K (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': "HR Organizational Chart",
    'version': '13.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'description': 'This module will give you the overall hierarchy of the HR department',
    'summary': 'This module will give you the overall hierarchy of the HR department',
    'author': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'company': 'Cybrosys Techno Solutions',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/org_chart_views.xml',
        'views/assets.xml',
    ],
    'qweb': [
        "static/src/xml/hr_org_chart_template.xml",
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
