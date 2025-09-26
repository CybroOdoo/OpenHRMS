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
    'name': "Open HRMS Service Request",
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': """For Requesting Services""",
    'description': """It allows employees to submit service requests related to 
     HR, such as IT support, asset maintenance, or administrative assistance.""",
    'author':  'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website':  'https://www.cybrosys.com',
    'depends': ['hr', 'stock', 'oh_employee_creation_from_user', 'project',
                'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'security/service_request_security.xml',
        'security/ohrms_service_request_groups.xml',
        'data/service_request_sequence.xml',
        'views/service_request_views.xml',
        'views/service_execute_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False,
}
