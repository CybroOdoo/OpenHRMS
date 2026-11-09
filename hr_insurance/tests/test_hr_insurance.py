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
"""Unit tests for the hr_insurance module."""
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrInsurance(TransactionCase):
    """Comprehensive test suite for HR Insurance module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        # Groups
        cls.group_user = cls.env.ref('base.group_user')
        cls.group_hr_user = cls.env.ref('hr.group_hr_user')
        cls.group_hr_manager = cls.env.ref('hr.group_hr_manager')

        # Test Users
        cls.user_employee = cls.env['res.users'].create({
            'name': 'Test Regular User',
            'login': 'test_reg_user',
            'email': 'reg_user@example.com',
            'group_ids': [(6, 0, [cls.group_user.id])],
        })
        cls.user_officer = cls.env['res.users'].create({
            'name': 'Test HR Officer',
            'login': 'test_hr_officer',
            'email': 'hr_officer@example.com',
            'group_ids': [(6, 0, [cls.group_user.id, cls.group_hr_user.id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Test HR Manager',
            'login': 'test_hr_manager',
            'email': 'hr_manager@example.com',
            'group_ids': [(6, 0, [cls.group_user.id, cls.group_hr_manager.id])],
        })

        # Test Insurance Provider Partner
        cls.provider = cls.env['res.partner'].create({
            'name': 'Global Life Insurance Corp',
            'email': 'info@globallife.example.com',
        })

        # Test Employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Insurance Test Employee',
            'work_email': 'ins_employee@example.com',
            'user_id': cls.user_employee.id,
            'company_id': cls.company.id,
        })
        cls.contract = cls.employee.version_id
        cls.structure_base = cls.env.ref('hr_payroll_community.structure_base')

        cls.date_from = fields.Date.today().replace(day=1)
        cls.date_to = (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()

        if cls.contract:
            cls.contract.write({
                'wage': 5000.0,
                'struct_id': cls.structure_base.id,
                'date_start': cls.date_from - timedelta(days=60),
            })

        # Test Insurance Policies
        cls.policy_monthly = cls.env['insurance.policy'].create({
            'name': 'Health Standard Monthly',
            'insurer_id': cls.provider.id,
            'group_policy_number': 'POL-M-001',
            'policy_coverage': 'monthly',
            'amount': 200.0,
            'sum_insured': 10000.0,
            'company_percentage': 50.0,
            'company_id': cls.company.id,
        })
        cls.policy_semi = cls.env['insurance.policy'].create({
            'name': 'Accident Semi-Annual',
            'insurer_id': cls.provider.id,
            'group_policy_number': 'POL-S-002',
            'policy_coverage': 'six_months',
            'amount': 600.0,
            'sum_insured': 25000.0,
            'company_percentage': 25.0,
            'company_id': cls.company.id,
        })
        cls.policy_annual = cls.env['insurance.policy'].create({
            'name': 'Life Comprehensive Annual',
            'insurer_id': cls.provider.id,
            'group_policy_number': 'POL-Y-003',
            'policy_coverage': 'yearly',
            'amount': 1200.0,
            'sum_insured': 50000.0,
            'company_percentage': 0.0,
            'company_id': cls.company.id,
        })

    def test_01_policy_creation_and_defaults(self):
        """Test insurance policy creation and fields default values."""
        policy = self.env['insurance.policy'].create({
            'name': 'Basic Dental',
            'amount': 100.0,
            'sum_insured': 5000.0,
        })
        self.assertEqual(policy.policy_coverage, 'monthly')
        self.assertEqual(policy.company_id, self.env.company)
        self.assertEqual(policy.amount, 100.0)
        self.assertEqual(policy.sum_insured, 5000.0)

    def test_02_insurance_computations_and_lifecycle(self):
        """Test insurance record computations, onchange, confirmation, and renewal."""
        insurance = self.env['hr.insurance'].new({
            'employee_id': self.employee.id,
            'policy_id': self.policy_monthly.id,
        })
        insurance._onchange_policy_id()
        self.assertEqual(insurance.policy_coverage, 'monthly')
        self.assertEqual(insurance.amount, 200.0)
        self.assertEqual(insurance.sum_insured, 10000.0)
        self.assertEqual(insurance.company_percentage, 50.0)
        self.assertTrue(insurance.date_from)

        # Create saved record
        rec = self.env['hr.insurance'].create({
            'employee_id': self.employee.id,
            'policy_id': self.policy_monthly.id,
            'policy_coverage': 'monthly',
            'amount': 200.0,
            'sum_insured': 10000.0,
            'company_percentage': 50.0,
            'date_from': self.date_from,
        })
        # Check computed net deduction: 200 - (200 * 50 / 100) = 100.0
        self.assertAlmostEqual(rec.deducted_amount, 100.0)

        # Check end date for monthly coverage
        expected_date_to = self.date_from + relativedelta(months=1, days=-1)
        self.assertEqual(rec.date_to, expected_date_to)

        # State is draft initially
        self.assertEqual(rec.state, 'draft')

        # Confirm policy -> active
        rec.action_confirm()
        self.assertEqual(rec.state, 'active')

        # Test six_months and yearly date_to computations
        rec.policy_coverage = 'six_months'
        self.assertEqual(rec.date_to, self.date_from + relativedelta(months=6, days=-1))

        rec.policy_coverage = 'yearly'
        self.assertEqual(rec.date_to, self.date_from + relativedelta(years=1, days=-1))

        # Check amount = 0 gives deducted_amount = 0
        rec.amount = 0.0
        self.assertEqual(rec.deducted_amount, 0.0)
        rec.amount = 200.0

        # Check employee insurance_ids relation
        self.assertIn(rec, self.employee.insurance_ids)

        # Expire policy and test renewal
        rec.state = 'expired'
        rec.is_deducted = True
        rec.action_renewal()
        self.assertEqual(rec.state, 'active')
        self.assertFalse(rec.is_deducted)
        self.assertEqual(rec.date_from, fields.Date.today())

    def test_03_status_computation(self):
        """Test _compute_status for active, future, and expired scenarios."""
        # Past policy
        past_from = fields.Date.today() - relativedelta(months=3)
        rec_past = self.env['hr.insurance'].create({
            'employee_id': self.employee.id,
            'policy_id': self.policy_monthly.id,
            'policy_coverage': 'monthly',
            'amount': 150.0,
            'sum_insured': 5000.0,
            'date_from': past_from,
            'state': 'active',
        })
        rec_past._compute_status()
        self.assertEqual(rec_past.state, 'expired')

        # Future policy
        future_from = fields.Date.today() + relativedelta(months=1)
        rec_future = self.env['hr.insurance'].create({
            'employee_id': self.employee.id,
            'policy_id': self.policy_monthly.id,
            'policy_coverage': 'monthly',
            'amount': 150.0,
            'sum_insured': 5000.0,
            'date_from': future_from,
            'state': 'draft',
        })
        rec_future._compute_status()
        self.assertEqual(rec_future.state, 'active')

    def test_04_cron_and_reminders(self):
        """Test cron job execution, status update, and reminder activities."""
        # Policy expiring exactly 7 days from today
        expiring_start = (
            fields.Date.today()
            + relativedelta(days=7)
            - relativedelta(months=1, days=-1)
        )
        expiring_insurance = self.env['hr.insurance'].create({
            'employee_id': self.employee.id,
            'policy_id': self.policy_monthly.id,
            'policy_coverage': 'monthly',
            'amount': 200.0,
            'sum_insured': 10000.0,
            'date_from': expiring_start,
            'state': 'active',
        })
        self.assertEqual(expiring_insurance.date_to, fields.Date.today() + relativedelta(days=7))

        # Run cron
        self.env['hr.insurance']._cron_update_insurance_status()

        # Verify activity was scheduled on the expiring record
        activity = self.env['mail.activity'].search([
            ('res_model', '=', 'hr.insurance'),
            ('res_id', '=', expiring_insurance.id),
        ])
        self.assertTrue(
            activity,
            "Activity should have been scheduled for policy expiring in 7 days.",
        )

        # Re-run cron to verify duplicate activities are not created
        self.env['hr.insurance']._cron_update_insurance_status()
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'hr.insurance'),
            ('res_id', '=', expiring_insurance.id),
        ])
        self.assertEqual(len(activities), 1, "Only one activity should be scheduled.")

    def test_05_payslip_deduction_flow(self):
        """Test insurance salary deduction integration with payslips."""
        if not self.contract:
            return

        insurance = self.env['hr.insurance'].create({
            'employee_id': self.employee.id,
            'policy_id': self.policy_monthly.id,
            'policy_coverage': 'monthly',
            'amount': 300.0,
            'sum_insured': 15000.0,
            'company_percentage': 20.0,
            'date_from': self.date_from,
            'state': 'active',
        })
        # net deduction = 300 - (300 * 20 / 100) = 240.0
        self.assertAlmostEqual(insurance.deducted_amount, 240.0)

        # Test get_inputs directly
        inputs = self.env['hr.payslip'].get_inputs(self.contract, self.date_from, self.date_to)
        insur_input = next((i for i in inputs if i.get('code') == 'INSUR'), None)
        self.assertIsNotNone(insur_input)
        self.assertAlmostEqual(insur_input['amount'], 240.0)

        # Create payslip
        payslip = self.env['hr.payslip'].create({
            'name': 'Insurance Deduction Payslip',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.structure_base.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        payslip.onchange_employee()
        payslip.action_compute_sheet()

        # Check line_ids for INSUR line
        insur_line = payslip.line_ids.filtered(lambda line: line.code == 'INSUR')
        self.assertTrue(insur_line, "Payslip lines should contain the INSUR rule line.")
        self.assertAlmostEqual(insur_line.total, -240.0)

        # Action payslip done -> mark insurance as deducted
        self.assertFalse(insurance.is_deducted)
        payslip.action_payslip_done()
        self.assertTrue(insurance.is_deducted)

        # On the next payslip, this insurance should NOT be deducted again
        inputs_next = self.env['hr.payslip'].get_inputs(
            self.contract,
            self.date_from + relativedelta(months=1),
            self.date_to + relativedelta(months=1),
        )
        insur_input_next = next((i for i in inputs_next if i.get('code') == 'INSUR'), None)
        self.assertEqual(insur_input_next.get('amount', 0), 0)

    def test_06_access_rights(self):
        """Test access rights for Base User, HR Officer, and HR Manager."""
        # Officer can create policy and insurance
        policy = self.env['insurance.policy'].with_user(self.user_officer).create({
            'name': 'Officer Policy',
            'amount': 120.0,
            'sum_insured': 4000.0,
        })
        self.assertTrue(policy.id)

        insurance = self.env['hr.insurance'].with_user(self.user_officer).create({
            'employee_id': self.employee.id,
            'policy_id': policy.id,
            'policy_coverage': 'monthly',
            'amount': 120.0,
            'sum_insured': 4000.0,
            'date_from': self.date_from,
        })
        self.assertTrue(insurance.id)

        # Manager can write and unlink
        insurance.with_user(self.user_manager).write({'amount': 130.0})
        self.assertEqual(insurance.amount, 130.0)

        # Regular user can read own insurance
        user_ins = self.env['hr.insurance'].with_user(self.user_employee).browse(insurance.id)
        self.assertEqual(user_ins.employee_id, self.employee)

        # Regular user cannot create insurance
        with self.assertRaises(AccessError):
            self.env['hr.insurance'].with_user(self.user_employee).create({
                'employee_id': self.employee.id,
                'policy_id': policy.id,
                'policy_coverage': 'monthly',
                'amount': 100.0,
                'sum_insured': 2000.0,
            })
