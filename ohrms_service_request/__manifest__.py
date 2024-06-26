# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Bhagyadev KP (odoo@cybrosys.com)
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
################################################################################
{
    'name': "Open HRMS Service Request",
    'version': '17.0.1.0.1',
    'category': 'Human Resources',
    'summary': """For Requesting Services""",
    'description': """Manages the Technical requirements of Employees""",
    'author':  'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website':  'https://www.cybrosys.com',
    'depends': ['hr', 'stock', 'oh_employee_creation_from_user', 'project',
                'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/service_request_sequence.xml',
        'views/service_request_views.xml',
        'views/service_execute_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
    'application': True,
}
