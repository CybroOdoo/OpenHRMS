# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Unnimaya C O (odoo@cybrosys.com)
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
###############################################################################
{
    'name': 'Open HRMS Legal Actions',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Helps to streamline and manage Legal actions effectively.""",
    'description': """Empowering seamless legal operations, this module 
     facilitates effective management of legal actions. Features include 
     centralized case tracking and tools for efficient and organized legal 
     processes.""",
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr'],
    'data': [
        'security/oh_hr_lawsuit_management_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/legal_action_views.xml',
        'views/court_court_views.xml',
        'views/res_partner_views.xml',
        'views/hr_employee_views.xml',
    ],
    'demo': ['demo/oh_hr_lawsuit_management_demo.xml'],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
