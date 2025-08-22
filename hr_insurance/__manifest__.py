# -*- coding: utf-8 -*-
#############################################################################
#   A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Raneesha M K (<https://www.cybrosys.com>)
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
    'name': 'Open HRMS Employee Insurance',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Employee Insurance Management for Open HRMS.""",
    'description': """Manages insurance amounts for employees to be deducted 
                      from salary""",
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': ['base', 'hr', 'hr_payroll_community',
                'hr_employee_updation',
                'hr_contract'],
    'data': [
        'data/hr_salary_rule_data.xml',
        'security/ir.model.access.csv',
        'security/hr_insurance_security.xml',
        'views/hr_employee_views.xml',
        'views/employee_insurance_views.xml',
        'views/insurance_policy_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
