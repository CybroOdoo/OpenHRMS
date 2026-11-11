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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
"""Unit test suite for attendance_regularization module."""
from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAttendanceRegularization(TransactionCase):
    """Test suite covering attendance regularization models, workflows,
    constraints, and security access."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref('base.group_user')
        cls.group_manager = cls.env.ref('hr_attendance.group_hr_attendance_manager')

        # Create standard test users
        cls.user_employee = cls.env['res.users'].create({
            'name': 'Test Regular Employee',
            'login': 'test_regular_employee@example.com',
            'email': 'test_regular_employee@example.com',
            'group_ids': [Command.set([cls.group_user.id])],
        })
        cls.user_other = cls.env['res.users'].create({
            'name': 'Test Other Employee',
            'login': 'test_other_employee@example.com',
            'email': 'test_other_employee@example.com',
            'group_ids': [Command.set([cls.group_user.id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Test Attendance Manager',
            'login': 'test_attendance_manager@example.com',
            'email': 'test_attendance_manager@example.com',
            'group_ids': [Command.set([cls.group_user.id, cls.group_manager.id])],
        })

        # Resolve or create corresponding employees
        cls.employee_1 = cls.user_employee.employee_id or cls.env['hr.employee'].search([
            ('user_id', '=', cls.user_employee.id),
        ], limit=1)
        if not cls.employee_1:
            cls.employee_1 = cls.env['hr.employee'].create({
                'name': 'Employee One',
                'user_id': cls.user_employee.id,
            })

        cls.employee_2 = cls.user_other.employee_id or cls.env['hr.employee'].search([
            ('user_id', '=', cls.user_other.id),
        ], limit=1)
        if not cls.employee_2:
            cls.employee_2 = cls.env['hr.employee'].create({
                'name': 'Employee Two',
                'user_id': cls.user_other.id,
            })

        cls.employee_manager = cls.user_manager.employee_id or cls.env['hr.employee'].search([
            ('user_id', '=', cls.user_manager.id),
        ], limit=1)
        if not cls.employee_manager:
            cls.employee_manager = cls.env['hr.employee'].create({
                'name': 'Manager Employee',
                'user_id': cls.user_manager.id,
            })

        # Ensure employee_id on users is set
        cls.user_employee.employee_id = cls.employee_1
        cls.user_other.employee_id = cls.employee_2
        cls.user_manager.employee_id = cls.employee_manager

        # Create test category
        cls.category = cls.env['reg.categories'].create({
            'type': 'Onsite Client Support',
        })

        cls.now = fields.Datetime.now()
        cls.from_date = cls.now - timedelta(hours=8)
        cls.to_date = cls.now

    def test_01_default_employee_id(self):
        """Test default employee resolution for current user."""
        attend_reg_model = self.env['attendance.regular'].with_user(self.user_employee)
        default_emp = attend_reg_model._default_employee_id()
        self.assertEqual(default_emp, self.employee_1.id)

        # Test fallback branch when env.user.employee_id is not directly set
        test_user = self.env['res.users'].create({
            'name': 'Fallback Test User',
            'login': 'test_fallback_user@example.com',
            'email': 'test_fallback_user@example.com',
            'group_ids': [Command.set([self.group_user.id])],
        })
        fallback_emp = test_user.employee_id or self.env['hr.employee'].search([
            ('user_id', '=', test_user.id),
        ], limit=1)
        if not fallback_emp:
            fallback_emp = self.env['hr.employee'].create({
                'name': 'Fallback Employee',
                'user_id': test_user.id,
            })
        test_user.write({'employee_id': False})
        default_fallback = self.env['attendance.regular'].with_user(test_user)._default_employee_id()
        self.assertEqual(default_fallback, fallback_emp.id)

        # Test when user has no linked employee at all
        user_no_emp = self.env['res.users'].create({
            'name': 'No Emp User',
            'login': 'test_no_emp@example.com',
            'email': 'test_no_emp@example.com',
            'group_ids': [Command.set([self.group_user.id])],
        })
        self.env['hr.employee'].search([('user_id', '=', user_no_emp.id)]).unlink()
        user_no_emp.write({'employee_id': False})
        default_none = self.env['attendance.regular'].with_user(user_no_emp)._default_employee_id()
        self.assertFalse(default_none)

    def test_02_dates_constraint(self):
        """Test validation constraint when To Date is earlier than From Date."""
        # Valid: from_date <= to_date
        reg = self.env['attendance.regular'].with_user(self.user_employee).create({
            'reg_category': self.category.id,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'reg_reason': 'Working at client site',
            'employee_id': self.employee_1.id,
        })
        self.assertTrue(reg.id)

        # Equal dates: valid
        reg_equal = self.env['attendance.regular'].with_user(self.user_employee).create({
            'reg_category': self.category.id,
            'from_date': self.from_date,
            'to_date': self.from_date,
            'reg_reason': 'Instant check-in/out regularize',
            'employee_id': self.employee_1.id,
        })
        self.assertTrue(reg_equal.id)

        # Invalid: from_date > to_date raises ValidationError
        with self.assertRaises(ValidationError):
            self.env['attendance.regular'].with_user(self.user_employee).create({
                'reg_category': self.category.id,
                'from_date': self.to_date,
                'to_date': self.from_date,
                'reg_reason': 'Invalid dates',
                'employee_id': self.employee_1.id,
            })

    def test_03_employee_constraint_regular_user(self):
        """Non-manager users must only create regularization for themselves."""
        # Creating for themselves works
        reg = self.env['attendance.regular'].with_user(self.user_employee).create({
            'reg_category': self.category.id,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'reg_reason': 'Self regularization',
            'employee_id': self.employee_1.id,
        })
        self.assertEqual(reg.employee_id, self.employee_1)

        # Creating for another employee is blocked by security / constraint
        with self.assertRaises((AccessError, ValidationError)):
            self.env['attendance.regular'].with_user(self.user_employee).create({
                'reg_category': self.category.id,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'reg_reason': 'Trying for colleague',
                'employee_id': self.employee_2.id,
            })

        # Test _check_employee_id Python constraint directly
        reg_other = self.env['attendance.regular'].sudo().create({
            'reg_category': self.category.id,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'reg_reason': 'Direct constraint check',
            'employee_id': self.employee_2.id,
        })
        with self.assertRaises(ValidationError):
            reg_other.with_user(self.user_employee)._check_employee_id()

    def test_04_employee_constraint_manager_and_admin(self):
        """Managers and superusers can create regularization for any employee."""
        # Attendance manager creating for employee_1
        reg_mgr = self.env['attendance.regular'].with_user(self.user_manager).create({
            'reg_category': self.category.id,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'reg_reason': 'Manager regularizing employee 1',
            'employee_id': self.employee_1.id,
        })
        self.assertEqual(reg_mgr.employee_id, self.employee_1)

        # Superuser creating for employee_2
        reg_admin = self.env['attendance.regular'].sudo().create({
            'reg_category': self.category.id,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'reg_reason': 'Admin regularizing employee 2',
            'employee_id': self.employee_2.id,
        })
        self.assertEqual(reg_admin.employee_id, self.employee_2)

    def test_05_workflow_actions(self):
        """Test submit, reject, and approve workflow."""
        reg = self.env['attendance.regular'].with_user(self.user_employee).create({
            'reg_category': self.category.id,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'reg_reason': 'Workflow test',
            'employee_id': self.employee_1.id,
        })
        self.assertEqual(reg.state, 'draft')

        # Submit
        reg.action_submit()
        self.assertEqual(reg.state, 'requested')

        # Reject
        reg.with_user(self.user_manager).action_reject()
        self.assertEqual(reg.state, 'reject')

        # Approve a new requested record
        approve_start = self.now - timedelta(days=2, hours=8)
        approve_end = self.now - timedelta(days=2)
        reg_approve = self.env['attendance.regular'].with_user(self.user_employee).create({
            'reg_category': self.category.id,
            'from_date': approve_start,
            'to_date': approve_end,
            'reg_reason': 'Approval test',
            'employee_id': self.employee_1.id,
        })
        reg_approve.action_submit()
        self.assertEqual(reg_approve.state, 'requested')

        reg_approve.with_user(self.user_manager).action_approve()
        self.assertEqual(reg_approve.state, 'approved')

        # Check hr.attendance creation
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_1.id),
            ('check_in', '=', approve_start),
            ('check_out', '=', approve_end),
            ('regularization', '=', True),
        ], limit=1)
        self.assertTrue(attendance, "An hr.attendance record must be created with regularization=True")
        self.assertTrue(attendance.regularization)

    def test_06_reg_categories_crud(self):
        """Test categories model creation, reading, and rec_name."""
        cat = self.env['reg.categories'].create({
            'type': 'Work From Home (Emergency)',
        })
        self.assertEqual(cat.type, 'Work From Home (Emergency)')
        self.assertEqual(cat.display_name, 'Work From Home (Emergency)')

        # Search by type
        found = self.env['reg.categories'].name_search('Emergency')
        found_ids = [res[0] for res in found]
        self.assertIn(cat.id, found_ids)

    def test_07_hr_attendance_regularization_field(self):
        """Test standard hr.attendance records have regularization boolean."""
        att = self.env['hr.attendance'].create({
            'employee_id': self.employee_1.id,
            'check_in': self.now - timedelta(days=5, hours=9),
            'check_out': self.now - timedelta(days=5, hours=1),
        })
        self.assertFalse(att.regularization)

        att.write({'regularization': True})
        self.assertTrue(att.regularization)

    def test_08_security_access(self):
        """Test access rules for regular users and managers."""
        # Regular user can read categories
        cats = self.env['reg.categories'].with_user(self.user_employee).search([])
        self.assertTrue(cats)

        # Regular user can create and read their own attendance regularization
        my_reg = self.env['attendance.regular'].with_user(self.user_employee).create({
            'reg_category': self.category.id,
            'from_date': self.now - timedelta(days=3, hours=4),
            'to_date': self.now - timedelta(days=3),
            'reg_reason': 'My site visit',
            'employee_id': self.employee_1.id,
        })
        read_regs = self.env['attendance.regular'].with_user(self.user_employee).search([
            ('id', '=', my_reg.id),
        ])
        self.assertEqual(len(read_regs), 1)

        # Regular user cannot see other employee's regularization records
        other_reg = self.env['attendance.regular'].with_user(self.user_other).create({
            'reg_category': self.category.id,
            'from_date': self.now - timedelta(days=4, hours=4),
            'to_date': self.now - timedelta(days=4),
            'reg_reason': 'Other site visit',
            'employee_id': self.employee_2.id,
        })
        read_other = self.env['attendance.regular'].with_user(self.user_employee).search([
            ('id', '=', other_reg.id),
        ])
        self.assertEqual(len(read_other), 0, "User must not see other employee's regularization record")

        # Manager can see both
        mgr_regs = self.env['attendance.regular'].with_user(self.user_manager).search([
            ('id', 'in', [my_reg.id, other_reg.id]),
        ])
        self.assertEqual(len(mgr_regs), 2, "Manager must be able to view all regularization records")
