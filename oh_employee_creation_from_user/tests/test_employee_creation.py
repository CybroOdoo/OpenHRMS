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
from odoo import Command
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestEmployeeCreation(TransactionCase):
    """Test suite for oh_employee_creation_from_user module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_us = cls.env.ref('base.us', raise_if_not_found=False)
        if not cls.country_us:
            cls.country_us = cls.env['res.country'].search([], limit=1)

    def test_01_single_user_employee_creation(self):
        """Test that creating a single user creates an employee."""
        user = self.env['res.users'].create({
            'name': 'Test Single Employee User',
            'login': 'test_single_emp_user_01@example.com',
            'email': 'test_single_emp_user_01@example.com',
            'phone': '+1 555-0199',
        })
        self.assertTrue(
            user.employee_id, "User should have an employee linked"
        )
        self.assertEqual(user.employee_id.name, user.name)
        self.assertEqual(user.employee_id.user_id, user)
        self.assertEqual(user.employee_id.work_email, user.email)
        self.assertEqual(user.employee_id.work_phone, user.phone)
        self.assertEqual(user.employee_id.work_contact_id, user.partner_id)
        self.assertEqual(user.employee_id.company_id, user.company_id)

    def test_02_user_with_partner_address(self):
        """Test employee creation when partner has full address details."""
        partner = self.env['res.partner'].create({
            'name': 'Partner With Address',
            'email': 'address_user_02@example.com',
            'phone': '+1 555-0248',
            'street': '742 Evergreen Terrace',
            'city': 'Springfield',
            'country_id': self.country_us.id if self.country_us else False,
        })
        user = self.env['res.users'].create({
            'name': 'Address User',
            'login': 'address_user_02@example.com',
            'email': 'address_user_02@example.com',
            'partner_id': partner.id,
        })
        employee = user.employee_id
        self.assertTrue(employee, "Employee must be created for the user")
        self.assertEqual(employee.private_street, '742 Evergreen Terrace')
        self.assertEqual(employee.private_city, 'Springfield')
        if self.country_us:
            self.assertEqual(employee.private_country_id, self.country_us)
        self.assertEqual(employee.private_phone, '+1 555-0248')
        self.assertEqual(employee.private_email, 'address_user_02@example.com')

    def test_03_batch_user_creation(self):
        """Test creating multiple users in a single create() call."""
        users = self.env['res.users'].create([
            {
                'name': 'Batch User Alpha',
                'login': 'batch_alpha_03@example.com',
                'email': 'batch_alpha_03@example.com',
            },
            {
                'name': 'Batch User Beta',
                'login': 'batch_beta_03@example.com',
                'email': 'batch_beta_03@example.com',
            },
        ])
        self.assertEqual(len(users), 2)
        for user in users:
            self.assertTrue(
                user.employee_id,
                f"User {user.name} must have a linked employee",
            )
            self.assertEqual(user.employee_id.name, user.name)
            self.assertEqual(user.employee_id.user_id, user)
        # Ensure separate employees were created for each user
        self.assertNotEqual(users[0].employee_id, users[1].employee_id)

    def test_04_user_with_existing_employee(self):
        """Test that no duplicate employee is created if already linked."""
        emp = self.env['hr.employee'].create({
            'name': 'Pre-existing Employee Test 04',
        })
        user = self.env['res.users'].create({
            'name': 'User For Existing Employee Test 04',
            'login': 'user_existing_emp_04@example.com',
            'create_employee_id': emp.id,
        })
        emp_count = self.env['hr.employee'].search_count(
            [('user_id', '=', user.id)]
        )
        self.assertEqual(
            emp_count, 1, "Exactly one employee should be linked to the user"
        )
        self.assertEqual(
            user.employee_id,
            emp,
            "User should be linked to the pre-existing employee",
        )

    def test_05_user_with_avatar_image(self):
        """Test that user avatar transfers to employee record."""
        # 1x1 transparent png
        dummy_png = (
            b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk'
            b'+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        user = self.env['res.users'].create({
            'name': 'Avatar User',
            'login': 'avatar_user_05@example.com',
            'email': 'avatar_user_05@example.com',
            'image_1920': dummy_png.decode('ascii'),
        })
        self.assertTrue(user.employee_id, "Employee should be created")
        self.assertTrue(
            user.employee_id.image_1920, "Employee should have avatar"
        )

    def test_06_res_users_view(self):
        """Test that res.users form view loads correctly with the field."""
        view_form = self.env['res.users'].get_views(
            [(self.env.ref('base.view_users_form').id, 'form')]
        )
        self.assertIn('employee_id', view_form['views']['form']['arch'])

    def test_07_portal_share_user_no_employee(self):
        """Test that portal (share) users do not get an employee created."""
        portal_user = self.env['res.users'].create({
            'name': 'Test Portal User',
            'login': 'test_portal_user_07@example.com',
            'email': 'test_portal_user_07@example.com',
            'group_ids': [
                Command.set([self.env.ref('base.group_portal').id])
            ],
        })
        self.assertTrue(portal_user.share, "User should be a share user")
        self.assertFalse(
            portal_user.employee_ids,
            "No employee should be created for portal users",
        )
        self.assertFalse(
            portal_user.employee_id,
            "User should have no linked employee",
        )
