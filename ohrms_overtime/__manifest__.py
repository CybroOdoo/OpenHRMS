# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
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
    'name': 'Open HRMS Overtime',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage employee overtime efficiently by tracking and analyzing.',
    'description': """This module provides a solution for streamline and 
     enhance the management of employee overtime within your organization. 
     This module empowers HR professionals and managers to efficiently track, 
     record, and analyze employee overtime""",
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr_attendance', 'project', 'hr_payroll_community'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_data.xml',
        'data/ir_sequence_data.xml',
        'views/hr_overtime_views.xml',
        'views/overtime_type_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
    ],
    'demo': ['data/hr_overtime_demo.xml'],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
