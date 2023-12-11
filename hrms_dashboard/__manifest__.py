# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
    'name': "Open HRMS HR Dashboard",
    'version': '17.0.1.0.1',
    'summary': """Open HRMS - HR Dashboard""",
    'description': """Open HRMS - HR Dashboard""",
    'category': 'Generic Modules/Human Resources',
    'live_test_url': 'https://youtu.be/XwGGvZbv6sc',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'hr_holidays', 'hr_timesheet', 'hr_payroll_community',
                'hr_attendance', 'hr_timesheet_attendance',
                'hr_recruitment', 'hr_resignation', 'event',
                'hr_reward_warning'],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [
        'security/ir.model.access.csv',
        'report/broadfactor.xml',
        'views/hr_leave_views.xml',
        'views/hrms_dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hrms_dashboard/static/src/css/hrms_dashboard.css',
            'hrms_dashboard/static/src/css/lib/nv.d3.css',
            'hrms_dashboard/static/src/js/hrms_dashboard.js',
            'hrms_dashboard/static/src/js/lib/d3.min.js',
            'hrms_dashboard/static/src/xml/hrms_dashboard.xml',
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js',
        ],
    },
    'images': ["static/description/banner.jpg"],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
