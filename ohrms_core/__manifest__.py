# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
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
    'name': 'Open HRMS Core',
    'version': '13.0.1.2.1',
    'summary': """Open HRMS Suit: It brings all Open HRMS modules""",
    'description': """Main module of Open HRMS, It brings all others into a single module, Payroll, Payroll Accounting,Expense,
                Dashboard, Employees, Employee Document, Resignation, Salary Advance, Loan Management, Gratuity, Service Request, Gosi, WPS Report, Reminder, Multi Company, Shift Management, Employee History,
                Branch Transfer, Employee Appraisal,Biometric Device, openhrms, hrms, Announcements, Insurance Management, Vacation Management,Employee Appreciations, Asset Custody, Employee Checklist, Entry and Exit Checklist, Disciplinary Actions, Attrition Rate, Document Expiry, Visa Expiry, Law Suit Management, Employee, Employee Training""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Cybrosys Techno solutions',
    'company': 'Cybrosys Techno Solutions',
    'live_test_url': 'https://youtube.com/playlist?list=PLeJtXzTubzj-wDm0a0hxMVwARk31n41yw',
    'website': "https://www.openhrms.com",
    'depends': ['web',
                'hr',
                'hr_payroll_account_community',
                'hr_gamification',
                'hr_employee_updation',
                'hr_recruitment',
                'hr_attendance',
                'hr_holidays',
                'hr_payroll_community',
                'hr_expense',
                'hr_leave_request_aliasing',
                'hr_timesheet',
                'oh_employee_creation_from_user',
                'oh_employee_documents_expiry',
                'hr_multi_company',
                'ohrms_loan_accounting',
                'ohrms_salary_advance',
                'hr_reminder',
                'hr_reward_warning',
                'hrms_dashboard',
                ],
    'data': [
        'views/menu_arrangement_view.xml',
        'views/hr_config_view.xml',
        'views/template_view.xml',
        'views/menu_item_form_inherit_view.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.gif'],
    'qweb': [
            'static/src/xml/link_view.xml',
            'static/templates/side_bar.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
