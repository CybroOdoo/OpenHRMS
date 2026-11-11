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
"""Unit test suite for employee_background module."""
from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestEmployeeVerification(TransactionCase):
    """Test suite covering employee background verification model, workflows,
    constraints, portal entry filtering, and security access."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref('base.group_user')
        cls.group_hr_user = cls.env.ref('hr.group_hr_user')
        cls.group_hr_manager = cls.env.ref('hr.group_hr_manager')

        # Test HR Users
        cls.user_hr_manager = cls.env['res.users'].create({
            'name': 'Test Background HR Manager',
            'login': 'test_bg_hr_manager@example.com',
            'email': 'test_bg_hr_manager@example.com',
            'group_ids': [Command.set([cls.group_user.id, cls.group_hr_manager.id])],
        })
        cls.user_hr_officer = cls.env['res.users'].create({
            'name': 'Test Background HR Officer',
            'login': 'test_bg_hr_officer@example.com',
            'email': 'test_bg_hr_officer@example.com',
            'group_ids': [Command.set([cls.group_user.id, cls.group_hr_user.id])],
        })

        # Agency Partner & Agency User
        cls.agency_partner = cls.env['res.partner'].create({
            'name': 'Verified Screening Agency',
            'email': 'screening_agency@example.com',
            'verification_agent': True,
        })
        cls.user_agency = cls.env['res.users'].create({
            'name': 'Agency Portal User',
            'login': 'agency_portal_user@example.com',
            'email': 'screening_agency@example.com',
            'partner_id': cls.agency_partner.id,
            'group_ids': [Command.set([cls.env.ref('base.group_portal').id])],
        })

        # Regular Non-Agency Partner
        cls.regular_partner = cls.env['res.partner'].create({
            'name': 'Regular Customer Partner',
            'email': 'regular_customer@example.com',
            'verification_agent': False,
        })
        cls.user_regular_portal = cls.env['res.users'].create({
            'name': 'Regular Portal User',
            'login': 'regular_portal_user@example.com',
            'email': 'regular_customer@example.com',
            'partner_id': cls.regular_partner.id,
            'group_ids': [Command.set([cls.env.ref('base.group_portal').id])],
        })

        # Work location / company address partner
        cls.work_address_partner = cls.env['res.partner'].create({
            'name': 'Main Branch Office',
            'street': '100 Enterprise Boulevard',
            'city': 'San Francisco',
        })

        # Test Employees
        cls.employee_with_address = cls.env['hr.employee'].create({
            'name': 'Candidate With Address',
            'work_email': 'candidate_addr@example.com',
            'private_street': '123 Baker Street',
            'private_city': 'London',
        })

        cls.employee_work_address = cls.env['hr.employee'].create({
            'name': 'Candidate Work Address',
            'work_email': 'candidate_work@example.com',
            'address_id': cls.work_address_partner.id,
        })

        cls.employee_no_address = cls.env['hr.employee'].create({
            'name': 'Candidate No Address',
            'work_email': 'candidate_none@example.com',
        })

        # Sample Resume Attachment
        cls.resume_attachment = cls.env['ir.attachment'].create({
            'name': 'Resume_Candidate.pdf',
            'type': 'binary',
            'raw': b'PDF Resume Content Dummy',
            'res_model': 'hr.employee',
            'res_id': cls.employee_no_address.id,
        })

        cls.today = fields.Date.context_today(cls.env.user)

    def test_01_create_and_sequence(self):
        """Test verification creation and automated sequence numbering."""
        rec = self.env['employee.verification'].with_user(self.user_hr_manager).create({
            'employee_id': self.employee_with_address.id,
        })
        self.assertTrue(rec.name, "Record must have an automated sequence name")
        self.assertTrue(rec.name.startswith('EV/'), f"Sequence name should start with EV/, got {rec.name}")
        self.assertEqual(rec.state, 'draft')
        self.assertEqual(rec.assigned_id, self.user_hr_manager)
        self.assertEqual(rec.assigned_date, self.today)

    def test_02_candidate_address_computation(self):
        """Test candidate address computation from private or work address."""
        # Case A: Private address on employee
        rec_private = self.env['employee.verification'].create({
            'employee_id': self.employee_with_address.id,
        })
        self.assertTrue(rec_private.has_candidate_address)
        self.assertEqual(rec_private.candidate_street, '123 Baker Street')
        self.assertEqual(rec_private.candidate_city, 'London')

        # Case B: Work address fallback
        rec_work = self.env['employee.verification'].create({
            'employee_id': self.employee_work_address.id,
        })
        self.assertTrue(rec_work.has_candidate_address)
        self.assertEqual(rec_work.candidate_street, '100 Enterprise Boulevard')
        self.assertEqual(rec_work.candidate_city, 'San Francisco')

        # Case C: No address
        rec_none = self.env['employee.verification'].create({
            'employee_id': self.employee_no_address.id,
        })
        self.assertFalse(rec_none.has_candidate_address)
        self.assertFalse(rec_none.candidate_street)

    def test_03_expected_date_constraint(self):
        """Test validation constraint when expected_date is earlier than assigned_date."""
        # Valid: Future expected date
        rec = self.env['employee.verification'].create({
            'employee_id': self.employee_with_address.id,
            'expected_date': self.today + timedelta(days=14),
        })
        self.assertTrue(rec.id)

        # Equal: Same date
        rec_equal = self.env['employee.verification'].create({
            'employee_id': self.employee_with_address.id,
            'expected_date': self.today,
        })
        self.assertTrue(rec_equal.id)

        # Invalid: Past expected date
        with self.assertRaises(ValidationError):
            self.env['employee.verification'].create({
                'employee_id': self.employee_with_address.id,
                'expected_date': self.today - timedelta(days=5),
            })

    def test_04_unlink_restriction(self):
        """Draft records can be deleted, but assigned or submitted cannot."""
        # Draft record can be deleted
        rec_draft = self.env['employee.verification'].create({
            'employee_id': self.employee_with_address.id,
        })
        rec_id = rec_draft.id
        rec_draft.unlink()
        self.assertFalse(self.env['employee.verification'].browse(rec_id).exists())

        # Assigned record cannot be deleted
        rec_assigned = self.env['employee.verification'].create({
            'employee_id': self.employee_with_address.id,
            'agency_id': self.agency_partner.id,
        })
        rec_assigned.action_assign_statusbar()
        self.assertEqual(rec_assigned.state, 'assign')

        with self.assertRaises(UserError):
            rec_assigned.unlink()

    def test_05_action_assign_statusbar(self):
        """Test assigning verification to an external agency."""
        rec = self.env['employee.verification'].create({
            'employee_id': self.employee_no_address.id,
        })

        # Missing agency raises UserError
        with self.assertRaises(UserError):
            rec.action_assign_statusbar()

        rec.agency_id = self.agency_partner

        # Missing both address and resume raises UserError
        with self.assertRaises(UserError):
            rec.action_assign_statusbar()

        # Attaching resume enables assignment
        rec.resume_ids = [Command.link(self.resume_attachment.id)]
        rec.action_assign_statusbar()
        self.assertEqual(rec.state, 'assign')
        self.assertTrue(self.resume_attachment.public, "Attached resume should be made public for portal agency")

    def test_06_res_partner_verification_agent(self):
        """Test verification_agent boolean field on res.partner."""
        self.assertTrue(self.agency_partner.verification_agent)
        self.assertFalse(self.regular_partner.verification_agent)

        agents = self.env['res.partner'].search([('verification_agent', '=', True)])
        self.assertIn(self.agency_partner, agents)
        self.assertNotIn(self.regular_partner, agents)

    def test_07_portal_entry_filtering(self):
        """Test portal.entry card visibility based on verification agent status."""
        entry = self.env.ref('employee_background.portal_employee_verification', raise_if_not_found=False)
        if not entry:
            return

        # Verification Agent sees the portal card
        visible_agent = entry.with_user(self.user_agency)._filter_visible_portal_cards()
        self.assertIn(entry, visible_agent)

        # Non-agent without assigned requests does not see the portal card
        visible_regular = entry.with_user(self.user_regular_portal)._filter_visible_portal_cards()
        self.assertNotIn(entry, visible_regular)

    def test_08_security_access(self):
        """Test access rules for HR Officer and HR Manager."""
        rec = self.env['employee.verification'].with_user(self.user_hr_manager).create({
            'employee_id': self.employee_with_address.id,
        })

        # HR Officer has read access
        read_officer = self.env['employee.verification'].with_user(self.user_hr_officer).search([
            ('id', '=', rec.id),
        ])
        self.assertEqual(len(read_officer), 1)

        # HR Manager has full access
        rec.with_user(self.user_hr_manager).write({'expected_date': self.today + timedelta(days=7)})
        self.assertEqual(rec.expected_date, self.today + timedelta(days=7))

        # Verify res.partner access rules
        partner_officer = self.env['res.partner'].with_user(self.user_hr_officer).search([
            ('id', '=', self.agency_partner.id),
        ])
        self.assertEqual(len(partner_officer), 1)
        self.assertTrue(partner_officer.verification_agent)

        self.agency_partner.with_user(self.user_hr_manager).write({'verification_agent': True})
        self.assertTrue(self.agency_partner.verification_agent)
