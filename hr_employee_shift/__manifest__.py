# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': "Open HRMS Employee Shift",
    'version': '18.0.1.0.0',
    'summary': """Easily create, manage, and track employee shift schedules.""",
    'description': """It helps manage and track employee shifts and schedule 
        them according to their contracts and work requirements.""",
    'live_test_url': 'https://youtu.be/o580wqD9Nig',
    'category': 'Human Resource',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr_payroll_community', 'resource'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_employee_shift_security.xml',
        'views/hr_employee_shift_views.xml',
        'views/hr_employee_contract_views.xml',
        'wizard/hr_generate_shift_views.xml',
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
    'images': ["static/description/banner.jpg"],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': True,
}
