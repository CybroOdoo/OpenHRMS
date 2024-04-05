# -- coding: utf-8 --
###############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
###############################################################################
{
    'name': "Open HRMS Vacation Management",
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Vacation Management,manages employee vacation""",
    'description': """The 'Vacation Management System' is a robust platform
     designed to streamline and optimize the management of employee 
     vacations within an organization.""",
    'live_test_url': 'https://youtu.be/Pf7zf-PkdfA',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com,https://cybrosys.com',
    'depends': ['hr_leave_request_aliasing', 'project',
                'hr_payroll_community', 'account'],
    'data': [
        'security/hr_flight_ticket_rule.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/hr_contribution_register_demo.xml',
        'data/hr_salary_rule_demo.xml',
        'data/mail_data_templates.xml',
        'data/res_partner_demo.xml',
        'views/hr_flight_ticket_views.xml',
        'views/hr_leave_views.xml',
        'views/hr_payslip_views.xml',
        'views/pending_task_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/task_reassign_views.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
