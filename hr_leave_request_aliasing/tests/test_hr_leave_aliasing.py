# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
#############################################################################
from datetime import date

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrLeaveAliasing(TransactionCase):
    """Test suite for hr_leave_request_aliasing module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_prefix', 'Leave')
        cls.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_domain', 'example.com')

        cls.manager_user = cls.env['res.users'].create({
            'name': 'Leave Manager',
            'login': 'leave_manager@example.com',
            'email': 'leave_manager@example.com',
            'group_ids': [Command.link(cls.env.ref('hr_holidays.group_hr_holidays_manager').id)],
        })

        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'work_email': 'john.doe@example.com',
            'leave_manager_id': cls.manager_user.id,
        })

        cls.user_employee = cls.env['res.users'].create({
            'name': 'User Employee',
            'login': 'user_emp@example.com',
            'email': 'user_emp@example.com',
        })
        cls.employee_with_user = cls.env['hr.employee'].create({
            'name': 'Employee with User',
            'user_id': cls.user_employee.id,
        })

        cls.work_entry_type = cls.env['hr.work.entry.type'].sudo().search([
            ('requires_allocation', '=', False),
        ], limit=1)
        if not cls.work_entry_type:
            cls.work_entry_type = cls.env['hr.work.entry.type'].sudo().create({
                'name': 'Test Unpaid Leave',
                'code': 'TEST_UNPAID',
                'requires_allocation': False,
            })

    def test_01_res_config_settings(self):
        """Test alias prefix and domain configuration in res.config.settings."""
        settings = self.env['res.config.settings'].create({
            'alias_prefix': 'TimeOff',
            'alias_domain': 'company.com',
        })
        settings.execute()
        prefix = self.env['ir.config_parameter'].sudo().get_str(
            'hr_holidays.alias_prefix', '')
        domain = self.env['ir.config_parameter'].sudo().get_str(
            'hr_holidays.alias_domain', '')
        self.assertEqual(prefix, 'TimeOff')
        self.assertEqual(domain, 'company.com')

    def test_02_leave_creation_single_date(self):
        """Test automated leave request generation with a single date."""
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_prefix', 'Leave')
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_domain', 'example.com')

        msg_dict = {
            'subject': 'Leave Request - Medical',
            'email_from': 'john.doe@example.com',
            'body': '<p>Hello, please approve leave for 15/11/2026.</p>',
        }
        leave = self.env['hr.leave'].message_new(msg_dict)
        self.assertTrue(leave)
        self.assertEqual(leave.employee_id, self.employee)
        self.assertEqual(leave.request_date_from, date(2026, 11, 15))
        self.assertEqual(leave.request_date_to, date(2026, 11, 15))

    def test_03_leave_creation_date_range(self):
        """Test automated leave request generation with start and end dates."""
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_prefix', 'Leave')
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_domain', 'example.com')

        msg_dict = {
            'subject': 'Leave for Vacations',
            'email_from': '"John Doe" <john.doe@example.com>',
            'body': '<div>Requesting leave from 10/12/2026 to 14/12/2026. Thanks!</div>',
        }
        leave = self.env['hr.leave'].message_new(msg_dict)
        self.assertTrue(leave)
        self.assertEqual(leave.employee_id, self.employee)
        self.assertEqual(leave.request_date_from, date(2026, 12, 10))
        self.assertEqual(leave.request_date_to, date(2026, 12, 14))

    def test_04_leave_creation_user_email_match(self):
        """Test matching employee by user_id email."""
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_prefix', 'Leave')
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_domain', 'example.com')

        msg_dict = {
            'subject': 'Leave - Urgent',
            'email_from': 'user_emp@example.com',
            'body': '<p>Off on 20/12/2026.</p>',
        }
        leave = self.env['hr.leave'].message_new(msg_dict)
        self.assertTrue(leave)
        self.assertEqual(leave.employee_id, self.employee_with_user)

    def test_05_leave_creation_no_dates_in_body(self):
        """Test incoming email when body contains no valid dates."""
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_prefix', 'Leave')
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_domain', 'example.com')

        msg_dict = {
            'subject': 'Leave - Question',
            'email_from': 'john.doe@example.com',
            'body': '<p>I would like to take leave next Monday.</p>',
        }
        leave = self.env['hr.leave'].message_new(msg_dict)
        self.assertTrue(leave)

    def test_06_leave_creation_non_matching_email(self):
        """Test incoming email from an outsider with no matching employee."""
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_prefix', 'SpecialLeave')
        self.env['ir.config_parameter'].sudo().set_str(
            'hr_holidays.alias_domain', 'specialcompany.com')

        msg_dict = {
            'subject': 'General Discussion',
            'email_from': 'outsider@otherdomain.com',
            'body': '<p>Meeting on 05/05/2026.</p>',
        }
        with self.assertRaises(UserError):
            self.env['hr.leave'].message_new(msg_dict)

    def test_07_leave_creation_labeled_dates(self):
        """Test leave creation with 'Date From:' and 'Date To:' labels in body."""
        msg_dict = {
            'subject': 'Leave Request',
            'email_from': 'john.doe@example.com',
            'body': '<p>Date From: 01/12/2026 and Date To: 05/12/2026</p>',
        }
        leave = self.env['hr.leave'].message_new(msg_dict)
        self.assertTrue(leave)
        self.assertEqual(leave.request_date_from, date(2026, 12, 1))
        self.assertEqual(leave.request_date_to, date(2026, 12, 5))
