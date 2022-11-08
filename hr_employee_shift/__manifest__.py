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
    'name': "Open HRMS Employee Shift",
    'version': '16.0.1.0.0',
    'summary': """Easily create, manage, and track employee shift schedules.""",
    'description': """Easily create, manage, and track employee shift schedules.""",
    'live_test_url': 'https://youtu.be/o580wqD9Nig',
    'category': 'Human Resource',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'hr_payroll_community', 'resource'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_employee_shift_security.xml',
        'views/hr_employee_shift_view.xml',
        'views/hr_employee_contract_view.xml',
        'views/hr_generate_shift_view.xml',
    ],
    'demo': [
        'demo/shift_schedule_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_employee_shift/static/src/css/shift_dashboard.css',
            'hr_employee_shift/static/src/less/shift_dashboard.less',
        ],
     },
    'images': ["static/description/banner.png"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
