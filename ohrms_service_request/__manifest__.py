# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Sayooj(<https://www.cybrosys.com>)
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
    'name': "Open HRMS Service Request",
    'version': '11.0.1.0.0',
    'summary': """For Requesting Service""",
    'description': """Requesting Services""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'stock','oh_employee_creation_from_user','project','hr_attendance'],
    'data': [
            'security/ir.model.access.csv',
             'security/security.xml',
             'views/service_view.xml',
             'views/sequence.xml',
            ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}

