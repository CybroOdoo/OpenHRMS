# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
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
    'name': 'Open HRMS Employee History',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Various Histories related to an employee. """,
    'description': """This module tracks the Job/Department History, Salary History, 
     Contract History and Hourly Cost History of the employees in a company""",
    'live_test_url': 'https://youtu.be/TaaDrBn3csc',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com, https://cybrosys.com",
    'depends': ['hr', 'hr_contract', 'oh_employee_creation_from_user'],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_history_views.xml',
        'views/department_history_views.xml',
        'views/hr_employee_views.xml',
        'views/salary_history_views.xml',
        'views/hourly_cost_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
