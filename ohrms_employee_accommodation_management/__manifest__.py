# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ranjith R(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
{
    'name': 'OHRMS Employee Accommodation Management',
    'version': '14.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Efficiently manage room allocation for employees.',
    'description': "This module allows administrators to manage the allocation "
                   "of rooms for employees in an organization. It includes "
                   "features such as the ability to input data about available "
                   "rooms and employees, generate room assignment "
                   "recommendations based on employee job roles and preferences"
                   ", and schedule and book rooms for meetings and events."
                   " With this module, organizations can save time and reduce "
                   "errors in the process of assigning rooms,"
                   " improving efficiency and productivity in the workplace.",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['base', 'mail', 'hr', 'web'],
    'data': [
        'security/ohrms_employee_accommodation_management_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/hr_allocation_transfer_views.xml',
        'views/hr_camps_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_rooms_views.xml',
        'wizards/hr_allocation_report_views.xml',
        'report/form_print_templates.xml',
        'report/hr_allocation_employee_templates.xml',
        'report/hr_allocation_type_templates.xml',
        'report/hr_allocation_reports.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
