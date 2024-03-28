# -*- coding: utf-8 -*-
#############################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
###############################################################################
{
    'name': 'Open HRMS Employee Background Verification',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Verify the background details of an Employee """,
    'description': """Manage the employees background verification Process 
    employee verification""",
    'live_test_url': 'https://youtu.be/mH5SzuKHa30',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['hr', 'hr_recruitment', 'mail', 'hr_employee_updation',
                'contacts', 'portal', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_verification_portal_templates.xml',
        'views/employee_verification_views.xml',
        'views/res_partner_views.xml',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
