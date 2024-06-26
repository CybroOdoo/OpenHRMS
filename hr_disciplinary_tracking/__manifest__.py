###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Name of Developer (odoo@cybrosys.com)
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
    'name': 'Open HRMS Disciplinary Tracking',
    'version': '17.0.1.0.1',
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
        'data/discipline_category_demo.xml',
        'data/hr_work_location_demo.xml',
        'data/hr_employee_demo.xml',
        'data/hr_department_demo.xml',
        'data/ir_sequence_data.xml',
        'data/disciplinary_action_demo.xml',
        'views/disciplinary_action_views.xml',
        'views/discipline_category_views.xml',
    ],
    'demo': ['data/disciplinary_action_demo.xml'],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
