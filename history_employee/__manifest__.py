# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Binu M Baiju(<https://www.cybrosys.com>)
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
    'version': '12.0.1.0.0',
    'summary': """History Of Employees In Your Company""",
    'description': 'Track the History of Employees in your Company',
    'category': 'Generic Modules/Human Resources',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'hr_contract', 'oh_employee_creation_from_user'],
    'data': ['views/employee_history.xml',
             'views/history_views.xml',
             'security/secure.xml',
             'security/ir.model.access.csv'
             ],
    'demo': [],
    'images': ['static/description/banner.gif'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
