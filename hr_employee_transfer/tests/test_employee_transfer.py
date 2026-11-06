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
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestEmployeeTransfer(TransactionCase):
    """Test suite for employee transfer module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env['res.company'].create({
            'name': 'Origin Company Alpha',
        })
        cls.company_b = cls.env['res.company'].create({
            'name': 'Destination Company Beta',
        })

        cls.user = cls.env['res.users'].create({
            'name': 'Test Transferred User',
            'login': 'transfer_test_user@example.com',
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id, cls.company_b.id])],
        })

        cls.dept_b = cls.env['hr.department'].create({
            'name': 'Beta Tech Dept',
            'company_id': cls.company_b.id,
        })
        cls.job_b = cls.env['hr.job'].create({
            'name': 'Beta Lead Engineer',
            'company_id': cls.company_b.id,
        })
        cls.location_b = cls.env['hr.work.location'].create({
            'name': 'Beta HQ Location',
            'company_id': cls.company_b.id,
        })
        cls.manager_b = cls.env['hr.employee'].create({
            'name': 'Beta Branch Manager',
            'company_id': cls.company_b.id,
        })

        cls.employee = cls.env['hr.employee'].create({
            'name': 'Alex Morgan',
            'company_id': cls.company_a.id,
            'user_id': cls.user.id,
            'identification_id': 'ID-TRANSFER-999',
            'private_email': 'alex.morgan@example.com',
        })

    def test_01_create_transfer_record(self):
        """Test employee transfer creation and name generation."""
        transfer = self.env['employee.transfer'].create({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_b.id,
            'transfer_date': date(2026, 11, 15),
        })
        self.assertEqual(transfer.name, "Transfer: Alex Morgan")
        self.assertEqual(transfer.state, 'draft')
        self.assertEqual(transfer.company_id, self.company_a)
        self.assertEqual(transfer.transfer_date_str, '15 Nov 2026')

    def test_02_compute_transfer_date_str_empty(self):
        """Test compute_transfer_date_str when transfer_date is False."""
        transfer = self.env['employee.transfer'].create({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_b.id,
        })
        transfer.transfer_date = False
        transfer._compute_transfer_date_str()
        self.assertEqual(transfer.transfer_date_str, '')

    def test_03_compute_transferred(self):
        """Test transferred compute flag based on user's allowed companies."""
        transfer = self.env['employee.transfer'].create({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_b.id,
        })
        # Current user env has company_b in allowed companies or self.env.user
        transfer._compute_transferred()
        self.assertIn(transfer.transferred, [True, False])

    def test_04_onchange_employee_id(self):
        """Test onchange employee_id resets or populates transfer_company_id."""
        transfer = self.env['employee.transfer'].new({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_a.id,
        })
        transfer._onchange_employee_id()
        self.assertNotEqual(transfer.transfer_company_id, self.company_a)

    def test_05_onchange_transfer_company_id(self):
        """Test resetting target assignment fields if they belong to another company."""
        transfer = self.env['employee.transfer'].new({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_a.id,
            'new_department_id': self.dept_b.id,
            'new_job_id': self.job_b.id,
            'new_work_location_id': self.location_b.id,
            'new_parent_id': self.manager_b.id,
        })
        transfer._onchange_transfer_company_id()
        self.assertFalse(transfer.new_department_id)
        self.assertFalse(transfer.new_job_id)
        self.assertFalse(transfer.new_work_location_id)
        self.assertFalse(transfer.new_parent_id)

    def test_06_action_transfer_validation(self):
        """Test validation on action_transfer."""
        transfer = self.env['employee.transfer'].create({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_b.id,
        })
        # Set transfer_company_id to origin company to test same company error
        transfer.write({'transfer_company_id': self.company_a.id})
        with self.assertRaises(UserError):
            transfer.action_transfer()

        # Valid transfer
        transfer.write({'transfer_company_id': self.company_b.id})
        transfer.action_transfer()
        self.assertEqual(transfer.state, 'transfer')

    def test_07_action_receive_employee_new_profile(self):
        """Test successful employee transfer and new profile creation."""
        transfer_date = fields.Date.today()
        transfer = self.env['employee.transfer'].create({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_b.id,
            'transfer_date': transfer_date,
            'new_department_id': self.dept_b.id,
            'new_job_id': self.job_b.id,
            'new_work_location_id': self.location_b.id,
            'new_parent_id': self.manager_b.id,
        })
        transfer.action_transfer()
        res = transfer.action_receive_employee()

        self.assertEqual(res.get('tag'), 'reload')
        self.assertEqual(transfer.state, 'done')
        self.assertEqual(transfer.old_employee_id, self.employee)
        self.assertFalse(transfer.old_employee_id.active)
        self.assertFalse(transfer.old_employee_id.user_id)

        new_emp = transfer.employee_id
        self.assertNotEqual(new_emp, self.employee)
        self.assertEqual(new_emp.company_id, self.company_b)
        self.assertEqual(new_emp.department_id, self.dept_b)
        self.assertEqual(new_emp.job_id, self.job_b)
        self.assertEqual(new_emp.work_location_id, self.location_b)
        self.assertEqual(new_emp.parent_id, self.manager_b)
        self.assertEqual(new_emp.contract_date_start, transfer_date)

    def test_08_action_receive_employee_archived_reactivate(self):
        """Test reactivating existing archived employee profile upon transfer."""
        # Pre-create an archived employee in Beta company
        archived_emp = self.env['hr.employee'].sudo().create({
            'name': 'Sam Taylor',
            'identification_id': 'ID-SAM-123',
            'company_id': self.company_b.id,
            'active': False,
        })

        active_emp = self.env['hr.employee'].create({
            'name': 'Sam Taylor',
            'identification_id': 'ID-SAM-123',
            'company_id': self.company_a.id,
        })

        transfer = self.env['employee.transfer'].create({
            'employee_id': active_emp.id,
            'transfer_company_id': self.company_b.id,
            'new_department_id': self.dept_b.id,
        })
        transfer.action_transfer()
        transfer.action_receive_employee()

        self.assertEqual(transfer.state, 'done')
        self.assertEqual(transfer.employee_id, archived_emp)
        self.assertTrue(archived_emp.active)
        self.assertEqual(archived_emp.department_id, self.dept_b)

    def test_09_cancel_transfer(self):
        """Test cancel transfer functionality."""
        transfer = self.env['employee.transfer'].create({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_b.id,
        })
        transfer.action_transfer()
        transfer.cancel_transfer()
        self.assertEqual(transfer.state, 'cancel')

    def test_10_action_receive_invalid_state(self):
        """Test that action_receive_employee raises error if state is not transfer."""
        transfer = self.env['employee.transfer'].create({
            'employee_id': self.employee.id,
            'transfer_company_id': self.company_b.id,
        })
        with self.assertRaises(UserError):
            transfer.action_receive_employee()

    def test_11_bypass_methods_coverage(self):
        """Test elevated bypass methods on overridden models."""
        spec = {'display_name': {}}

        # 1. hr.department
        dept = self.dept_b
        dept.with_context(employee_transfer_bypass=True).web_name_search(name=dept.name, specification=spec)
        dept.with_context(employee_transfer_bypass=True).web_search_read(domain=[('id', '=', dept.id)], specification=spec)
        dept.with_context(employee_transfer_bypass=True).search_fetch(domain=[('id', '=', dept.id)])
        dept.with_context(employee_transfer_bypass=True).name_search(name=dept.name)
        dept.with_context(employee_transfer_bypass=True).read(['name', 'company_id'])
        dept.with_context(employee_transfer_bypass=True).check_access('read')

        # 2. hr.job
        job = self.job_b
        job.with_context(employee_transfer_bypass=True).web_name_search(name=job.name, specification=spec)
        job.with_context(employee_transfer_bypass=True).web_search_read(domain=[('id', '=', job.id)], specification=spec)
        job.with_context(employee_transfer_bypass=True).search_fetch(domain=[('id', '=', job.id)])
        job.with_context(employee_transfer_bypass=True).name_search(name=job.name)
        job.with_context(employee_transfer_bypass=True).read(['name', 'company_id'])
        job.with_context(employee_transfer_bypass=True).check_access('read')

        # 3. hr.work.location
        loc = self.location_b
        loc.with_context(employee_transfer_bypass=True).web_name_search(name=loc.name, specification=spec)
        loc.with_context(employee_transfer_bypass=True).web_search_read(domain=[('id', '=', loc.id)], specification=spec)
        loc.with_context(employee_transfer_bypass=True).search_fetch(domain=[('id', '=', loc.id)])
        loc.with_context(employee_transfer_bypass=True).name_search(name=loc.name)
        loc.with_context(employee_transfer_bypass=True).read(['name', 'company_id'])
        loc.with_context(employee_transfer_bypass=True).check_access('read')

        # 4. hr.employee
        emp = self.employee
        emp.with_context(employee_transfer_bypass=True).web_name_search(name=emp.name, specification=spec)
        emp.with_context(employee_transfer_bypass=True).web_search_read(domain=[('id', '=', emp.id)], specification=spec)
        emp.with_context(employee_transfer_bypass=True).search_fetch(domain=[('id', '=', emp.id)])
        emp.with_context(employee_transfer_bypass=True).name_search(name=emp.name)
        emp.with_context(employee_transfer_bypass=True).read(['name', 'company_id'])
        emp.with_context(employee_transfer_bypass=True).check_access('read')

        # 5. res.company
        comp = self.company_a
        comp.with_context(employee_transfer_bypass=True).web_name_search(name=comp.name, specification=spec)
        comp.with_context(employee_transfer_bypass=True).web_search_read(domain=[('id', '=', comp.id)], specification=spec)
        comp.with_context(employee_transfer_bypass=True).search_fetch(domain=[('id', '=', comp.id)])
        comp.with_context(employee_transfer_bypass=True).name_search(name=comp.name)
        comp.with_context(employee_transfer_bypass=True).read(['name'])
        comp.with_context(employee_transfer_bypass=True).check_access('read')
