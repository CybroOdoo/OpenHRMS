# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
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
################################################################################
{
    'name': 'Open HRMS Disciplinary Tracking',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Employee Disciplinary Tracking Management""",
    'description': """The primary goal of disciplinary tracking is to ensure 
     that employees adhere to company policies and regulations, and when 
     violations occur, to address them appropriately.""",
    'live_test_url': 'https://youtu.be/LFuw2iY4Deg',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['mail', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_disciplinary_tracking_security.xml',
        'data/ir_sequence_data.xml',
        'views/disciplinary_action_views.xml',
        'views/discipline_category_views.xml',
    ],
    'demo': [
        'data/disciplinary_action_demo.xml',
        'data/hr_department_demo.xml',
        'data/hr_employee_demo.xml'
        'data/hr_work_location_demo.xml',
        'data/discipline_category_demo.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
