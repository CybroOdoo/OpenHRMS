# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys (<https://www.cybrosys.com>)
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
    'name': "Open HRMS Attendance Regularization",
    'version': '16.0.1.0.0',
    'summary': """Assigning Attendance for the Employees with Onsight Jobs""",
    'description': """Assigning Attendance for the Employees with Onsight Jobs through the requests by Employees """,
    'live_test_url': 'https://youtu.be/6VN13PG5g_w',
    'category': 'Human Resource',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'hr_attendance', 'project', 'contacts', 'oh_employee_creation_from_user'],
    'data': [
            'security/ir.model.access.csv',
            'security/security.xml',
            'views/category.xml',
            'views/regularization_views.xml',
            ],
    'demo': ['data/regularization_data.xml'],
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
