# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
    'name': 'Open HRMS Core',
    'version': '17.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """Open HRMS Odoo17, HRMS odoo17, Odoo HR, HR Dashboard, Odoo17 Payroll, HR Management, Odoo Branch, Odoo Loan, Salary Advance, Odoo17,Payroll,Dashboard,Accounting,HR Kit,HR,Odoo Apps""",
    'description': """Openhrms, Main module of Open HRMS,Payroll, Payroll Accounting, Expense, Dashboard,
    Employees, Employee Document, Resignation, Salary Advance, Loan Management, 
    Gratuity, Service Request, Gosi, WPS Report, Reminder, Multi Company, 
    Shift Management, Employee History, Branch Transfer, Employee Appraisal,
    Biometric Device, Announcements, Insurance Management, Vacation Management,
    Employee Appreciations, Asset Custody, Employee Checklist, Entry and Exit 
    Checklist, Disciplinary Actions, openhrms, Open HRMS, hrms, Attrition Rate, 
    Document Expiry, Visa Expiry, Law Suit Management, Employee, Employee Training, payroll, odoo17 payroll""",
    'author': 'Cybrosys Techno solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'live_test_url': 'https://youtu.be/kBBlUFofCTs',
    'website': "https://www.openhrms.com",
    'depends': [
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
        'hr_reward_warning',
        'hrms_dashboard',
        'hr_reminder'
    ],
    'data': [
        'views/menu_arrangement_view.xml',
        'views/hr_config_view.xml',
        'views/menu_item_form_inherit_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ohrms_core/static/src/css/menu_order_alphabets.css',
            'ohrms_core/static/src/js/appMenu.js',
            'ohrms_core/static/src/xml/link_view.xml',
            'ohrms_core/static/templates/side_bar.xml'
        ],
    },
    "external_dependencies": {"python": ["pandas"]},
    'images': ['static/description/banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
