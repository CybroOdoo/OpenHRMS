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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged, TransactionCase


@tagged("post_install", "-at_install")
class TestHrPayrollCommunity(TransactionCase):
    """Test suite for the hr_payroll_community module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.user = cls.env.user

        # Create test employee
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Payroll Test Employee",
                "work_email": "test.employee@example.com",
            }
        )
        cls.contract = cls.employee.version_id
        cls.structure_base = cls.env.ref("hr_payroll_community.structure_base")

        cls.date_from = fields.Date.today().replace(day=1)
        cls.date_to = (
            datetime.now() + relativedelta(months=+1, day=1, days=-1)
        ).date()

        cls.contract.write(
            {
                "wage": 4000.0,
                "struct_id": cls.structure_base.id,
                "date_start": cls.date_from - timedelta(days=60),
                "date_end": cls.date_to + timedelta(days=60),
                "hra": 600.0,
                "travel_allowance": 250.0,
                "da": 150.0,
                "meal_allowance": 100.0,
                "medical_allowance": 80.0,
                "other_allowance": 50.0,
            }
        )

    def test_01_salary_rule_category(self):
        """Test hr.salary.rule.category creation, hierarchy, and cycle constraint."""
        parent_cat = self.env["hr.salary.rule.category"].create(
            {
                "name": "Test Parent Category",
                "code": "TPCAT",
            }
        )
        child_cat = self.env["hr.salary.rule.category"].create(
            {
                "name": "Test Child Category",
                "code": "TCAT",
                "parent_id": parent_cat.id,
            }
        )
        self.assertEqual(child_cat.parent_id, parent_cat)
        self.assertIn(child_cat, parent_cat.children_ids)

        with self.assertRaises(ValidationError):
            parent_cat.parent_id = child_cat

    def test_02_contribution_register(self):
        """Test hr.contribution.register model."""
        reg = self.env["hr.contribution.register"].create(
            {
                "name": "Test Health Register",
                "note": "Monthly healthcare fund",
                "partner_id": self.employee.work_contact_id.id,
            }
        )
        self.assertTrue(reg.id)
        self.assertEqual(reg.name, "Test Health Register")

    def test_03_salary_rule_and_conditions(self):
        """Test salary rule definitions, amount calculations, and conditions."""
        cat_alw = self.env.ref("hr_payroll_community.ALW")
        cat_ded = self.env.ref("hr_payroll_community.DED")

        # Fix amount rule
        rule_fix = self.env["hr.salary.rule"].create(
            {
                "name": "Bonus Fixed",
                "code": "BF",
                "category_id": cat_alw.id,
                "sequence": 10,
                "amount_select": "fix",
                "amount_fix": 250.0,
                "quantity": "1.0",
            }
        )
        localdict = {"contract": self.contract, "employee": self.employee}
        amt, qty, rate = rule_fix._compute_rule(localdict)
        self.assertEqual(amt, 250.0)
        self.assertEqual(qty, 1.0)
        self.assertEqual(rate, 100.0)

        # Percentage amount rule
        rule_pct = self.env["hr.salary.rule"].create(
            {
                "name": "Provident Fund 10%",
                "code": "PF10",
                "category_id": cat_ded.id,
                "sequence": 11,
                "amount_select": "percentage",
                "amount_percentage": 10.0,
                "amount_percentage_base": "contract.wage",
                "quantity": "1.0",
            }
        )
        amt, qty, rate = rule_pct._compute_rule(localdict)
        self.assertEqual(amt, 4000.0)
        self.assertEqual(rate, 10.0)

        # Python amount rule
        rule_py = self.env["hr.salary.rule"].create(
            {
                "name": "Custom Allowance",
                "code": "CA_PY",
                "category_id": cat_alw.id,
                "sequence": 12,
                "amount_select": "code",
                "amount_python_compute": "result = contract.wage * 0.05\nresult_qty = 2.0\nresult_rate = 100.0",
            }
        )
        amt, qty, rate = rule_py._compute_rule(localdict)
        self.assertEqual(amt, 200.0)
        self.assertEqual(qty, 2.0)

        # Range condition
        rule_range = self.env["hr.salary.rule"].create(
            {
                "name": "High Earner Bonus",
                "code": "HEB",
                "category_id": cat_alw.id,
                "sequence": 13,
                "condition_select": "range",
                "condition_range": "contract.wage",
                "condition_range_min": 3000.0,
                "condition_range_max": 10000.0,
                "amount_select": "fix",
                "amount_fix": 500.0,
            }
        )
        self.assertTrue(rule_range._satisfy_condition(localdict))
        rule_range.condition_range_min = 5000.0
        self.assertFalse(rule_range._satisfy_condition(localdict))

        # Python condition
        rule_py_cond = self.env["hr.salary.rule"].create(
            {
                "name": "Conditional HRA",
                "code": "CHRA",
                "category_id": cat_alw.id,
                "sequence": 14,
                "condition_select": "python",
                "condition_python": "result = contract.hra > 500.0",
                "amount_select": "fix",
                "amount_fix": 150.0,
            }
        )
        self.assertTrue(rule_py_cond._satisfy_condition(localdict))

        # Test error handling on bad formulas
        rule_bad_qty = self.env["hr.salary.rule"].create(
            {
                "name": "Bad Qty",
                "code": "BQ",
                "category_id": cat_alw.id,
                "amount_select": "fix",
                "amount_fix": 100.0,
                "quantity": "undefined_var + 1",
            }
        )
        with self.assertRaises(UserError):
            rule_bad_qty._compute_rule(localdict)

        rule_bad_pct = self.env["hr.salary.rule"].create(
            {
                "name": "Bad Pct Base",
                "code": "BPCT",
                "category_id": cat_alw.id,
                "amount_select": "percentage",
                "amount_percentage": 5.0,
                "amount_percentage_base": "undefined_var * 2",
            }
        )
        with self.assertRaises(UserError):
            rule_bad_pct._compute_rule(localdict)

        rule_bad_code = self.env["hr.salary.rule"].create(
            {
                "name": "Bad Code",
                "code": "BC",
                "category_id": cat_alw.id,
                "amount_select": "code",
                "amount_python_compute": "result = non_existent_variable",
            }
        )
        with self.assertRaises(UserError):
            rule_bad_code._compute_rule(localdict)

        rule_bad_range = self.env["hr.salary.rule"].create(
            {
                "name": "Bad Range",
                "code": "BR",
                "category_id": cat_alw.id,
                "condition_select": "range",
                "condition_range": "bad_syntax /",
            }
        )
        with self.assertRaises(UserError):
            rule_bad_range._satisfy_condition(localdict)

        rule_bad_py_cond = self.env["hr.salary.rule"].create(
            {
                "name": "Bad Py Cond",
                "code": "BPC",
                "category_id": cat_alw.id,
                "condition_select": "python",
                "condition_python": "syntax error @@@",
            }
        )
        with self.assertRaises(UserError):
            rule_bad_py_cond._satisfy_condition(localdict)

    def test_04_payroll_structure(self):
        """Test hr.payroll.structure methods, hierarchy, and recursion cycle check."""
        struct_child = self.env["hr.payroll.structure"].create(
            {
                "name": "Child Structure",
                "code": "CSTRUCT",
                "parent_id": self.structure_base.id,
            }
        )
        self.assertIn(struct_child, self.structure_base.children_ids)
        parent_structs = struct_child._get_parent_structure()
        self.assertIn(self.structure_base, parent_structs)

        # Structure copy
        copied = struct_child.copy()
        self.assertTrue(copied.name)
        self.assertIn("(copy)", copied.code)

        # Recursion check
        with self.assertRaises(ValidationError):
            self.structure_base.parent_id = struct_child

        # get_all_rules
        all_rules = (struct_child._get_parent_structure()).get_all_rules()
        self.assertTrue(len(all_rules) > 0)

    def test_05_hr_version_and_structure_types(self):
        """Test hr.version contracts and hr.payroll.structure.type."""
        struct_type = self.env["hr.payroll.structure.type"].create(
            {
                "name": "Custom Structure Type",
                "default_struct_id": self.structure_base.id,
            }
        )
        self.assertEqual(struct_type.default_struct_id, self.structure_base)

        structures = self.contract.get_all_structures()
        self.assertIn(self.structure_base.id, structures)

    def test_06_payslip_full_lifecycle(self):
        """Test full payslip creation, onchanges, calculations, workflow, and email."""
        payslip = self.env["hr.payslip"].create(
            {
                "name": "Salary Slip Test",
                "employee_id": self.employee.id,
                "contract_id": self.contract.id,
                "struct_id": self.structure_base.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )
        self.assertEqual(payslip.state, "draft")

        # Trigger onchanges
        payslip.onchange_employee()
        payslip.onchange_contract_id()
        payslip.onchange_date_from()
        payslip.onchange_date_to()

        # Legacy onchange_employee_id
        res_onchange = payslip.onchange_employee_id(
            self.date_from, self.date_to, self.employee.id, self.contract.id
        )
        self.assertIn("value", res_onchange)

        # Check worked day helper methods
        payroll_days = payslip._get_payroll_days(
            self.contract, self.date_from, self.date_to
        )
        self.assertEqual(payroll_days, 30.0)
        daily_rate = payslip._get_daily_rate(
            self.contract, self.date_from, self.date_to
        )
        self.assertAlmostEqual(daily_rate, 4000.0 / 30.0, places=2)
        paid_amount = payslip.paid_amount
        self.assertGreaterEqual(paid_amount, 0.0)

        # Date constraint
        with self.assertRaises(ValidationError):
            payslip.write({"date_from": self.date_to + timedelta(days=5)})
        payslip.write({"date_from": self.date_from})

        # Compute sheet
        payslip.action_compute_sheet()
        self.assertTrue(payslip.number)
        self.assertGreater(len(payslip.line_ids), 0)
        self.assertEqual(payslip.payslip_count, len(payslip.line_ids))

        # Check wages
        self.assertGreater(payslip.basic_wage, 0)
        self.assertGreater(payslip.gross_wage, 0)
        self.assertGreater(payslip.net_wage, 0)

        # get_salary_line_total
        basic_total = payslip.get_salary_line_total("BASIC")
        self.assertEqual(basic_total, payslip.basic_wage)
        self.assertEqual(payslip.get_salary_line_total("NON_EXISTENT"), 0.0)

        # Action send email composer context
        send_action = payslip.action_payslip_send()
        self.assertEqual(send_action["res_model"], "mail.compose.message")

        # Validate payslip (action_payslip_done)
        self.env["ir.config_parameter"].sudo().set_bool(
            "send_payslip_by_email", True
        )
        payslip.action_payslip_done()
        self.assertEqual(payslip.state, "done")
        self.assertTrue(payslip.is_send_mail)

        # Cannot delete done payslip
        with self.assertRaises(UserError):
            payslip.unlink()

        # Mark as paid
        payslip.action_mark_as_paid()
        self.assertEqual(payslip.state, "paid")

        # Cancel and reset to draft
        payslip.action_payslip_cancel()
        self.assertEqual(payslip.state, "cancel")
        payslip.action_payslip_draft()
        self.assertEqual(payslip.state, "draft")

        # Unlink draft payslip succeeds
        draft_copy = payslip.copy()
        draft_copy.action_compute_sheet()
        self.assertTrue(draft_copy.unlink())

    def test_07_payslip_refund(self):
        """Test payslip refund sheet functionality for single and multiple slips."""
        payslip1 = self.env["hr.payslip"].create(
            {
                "name": "Payslip 1",
                "employee_id": self.employee.id,
                "contract_id": self.contract.id,
                "struct_id": self.structure_base.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )
        payslip1.action_compute_sheet()

        # Single refund
        refund_act = payslip1.action_refund_sheet()
        self.assertEqual(refund_act["res_model"], "hr.payslip")
        refund_slip = self.env["hr.payslip"].browse(refund_act["res_id"])
        self.assertTrue(refund_slip.credit_note)
        self.assertIn("Refund", refund_slip.name)

        # Multiple refund
        payslip2 = self.env["hr.payslip"].create(
            {
                "name": "Payslip 2",
                "employee_id": self.employee.id,
                "contract_id": self.contract.id,
                "struct_id": self.structure_base.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )
        payslip2.action_compute_sheet()
        multi_refund_act = (payslip1 | payslip2).action_refund_sheet()
        self.assertEqual(multi_refund_act["view_mode"], "list,form")

    def test_08_payslip_lines_and_worked_days(self):
        """Test payslip lines, worked days, inputs, and browsable objects in safe_eval."""
        payslip = self.env["hr.payslip"].create(
            {
                "name": "Detailed Lines Test",
                "employee_id": self.employee.id,
                "contract_id": self.contract.id,
                "struct_id": self.structure_base.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )
        payslip.onchange_employee()

        # Add manual input
        input_line = self.env["hr.payslip.input"].create(
            {
                "name": "Overtime Input",
                "code": "OT",
                "payslip_id": payslip.id,
                "contract_id": self.contract.id,
                "amount": 300.0,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )
        self.assertTrue(input_line.id)

        # Add worked day line
        worked_day = self.env["hr.payslip.worked.days"].create(
            {
                "name": "Normal Work Days",
                "code": "WORK100",
                "payslip_id": payslip.id,
                "contract_id": self.contract.id,
                "number_of_days": 22.0,
                "number_of_hours": 176.0,
                "amount": 3000.0,
            }
        )
        self.assertTrue(worked_day.id)

        # Compute sheet
        payslip.action_compute_sheet()
        line = payslip.line_ids[:1]
        self.assertTrue(line)
        self.assertGreater(line.total, 0)

        # Test payslip line creation validation without contract
        with self.assertRaises(UserError):
            self.env["hr.payslip.line"].create(
                {
                    "name": "Invalid Line",
                    "code": "INV",
                    "salary_rule_id": line.salary_rule_id.id,
                    "category_id": line.category_id.id,
                    "slip_id": False,
                    "contract_id": False,
                }
            )

    def test_09_payslip_run_batch(self):
        """Test hr.payslip.run batch workflow and mass confirmations."""
        batch = self.env["hr.payslip.run"].create(
            {
                "name": "Batch October",
                "date_start": self.date_from,
                "date_end": self.date_to,
            }
        )
        self.assertEqual(batch.state, "draft")

        # Confirming empty batch raises error
        with self.assertRaises(UserError):
            batch.action_confirm_payslips()

        # Add payslip to batch
        payslip = self.env["hr.payslip"].create(
            {
                "name": "Batch Slip 1",
                "employee_id": self.employee.id,
                "contract_id": self.contract.id,
                "struct_id": self.structure_base.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "payslip_run_id": batch.id,
            }
        )
        payslip.action_compute_sheet()

        batch.action_confirm_payslips()
        self.assertEqual(batch.state, "done")
        self.assertEqual(payslip.state, "done")

        batch.action_mark_as_paid()
        self.assertEqual(batch.state, "paid")
        self.assertEqual(payslip.state, "paid")

        batch.action_payslip_run()
        self.assertEqual(batch.state, "draft")
        self.assertEqual(payslip.state, "draft")

        batch.action_cancel_payslips()
        self.assertEqual(batch.state, "cancel")
        self.assertEqual(payslip.state, "cancel")

    def test_10_wizards(self):
        """Test wizards: hr_payslip_run_generate, hr_payslips_employees, payslip_confirm, and contribution register report wizard."""
        batch = self.env["hr.payslip.run"].create(
            {
                "name": "Wizard Batch",
                "date_start": self.date_from,
                "date_end": self.date_to,
            }
        )

        # Wizard 1: hr.payslip.run.generate
        run_gen = (
            self.env["hr.payslip.run.generate"]
            .with_context(active_id=batch.id, active_model="hr.payslip.run")
            .create(
                {
                    "struct_id": self.structure_base.id,
                }
            )
        )
        self.assertEqual(run_gen.payslip_run_id, batch)
        continue_action = run_gen.action_continue()
        self.assertEqual(continue_action["res_model"], "hr.payslip.employees")

        # Wizard 2: hr.payslip.employees
        emp_wizard = (
            self.env["hr.payslip.employees"]
            .with_context(active_id=batch.id, active_ids=[batch.id])
            .create(
                {
                    "employee_ids": [(6, 0, [self.employee.id])],
                    "structure_id": self.structure_base.id,
                }
            )
        )
        # Select line
        if emp_wizard.line_ids:
            emp_wizard.line_ids.is_selected = True
        emp_wizard.action_compute_sheet()
        self.assertTrue(len(batch.slip_ids) > 0)

        # Wizard 3: payslip.confirm
        slip = batch.slip_ids[0]
        slip.action_compute_sheet()
        self.assertEqual(slip.state, "draft")
        confirm_wizard = (
            self.env["payslip.confirm"]
            .with_context(active_ids=[slip.id])
            .create({})
        )
        confirm_wizard.confirm_payslip()
        self.assertEqual(slip.state, "done")

        # Wizard 4: payslip.lines.contribution.register
        reg = self.env.ref(
            "hr_payroll_community.contribution_register_employees"
        )
        reg_wizard = (
            self.env["payslip.lines.contribution.register"]
            .with_context(active_ids=[reg.id])
            .create(
                {
                    "date_from": self.date_from,
                    "date_to": self.date_to,
                }
            )
        )
        report_action = reg_wizard.action_print_report()
        self.assertTrue(report_action)

    def test_11_hr_employee_and_settings(self):
        """Test hr.employee payslip count and res.config.settings."""
        # Employee payslip count
        self.assertGreaterEqual(self.employee.payslip_count, 0)
        self.assertTrue(hasattr(self.employee, "slip_ids"))

        # Config settings
        settings = self.env["res.config.settings"].create(
            {
                "send_payslip_by_email": True,
            }
        )
        settings.execute()
        val = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_bool("send_payslip_by_email")
        )
        self.assertTrue(val)

        # Work entry type
        work_entry_type = self.env["hr.work.entry.type"].search([], limit=1)
        if work_entry_type:
            work_entry_type.write({"is_paid": True})
            self.assertTrue(work_entry_type.is_paid)

    def test_12_reports(self):
        """Test SQL report hr.payslip.report and abstract QWeb report models."""
        # hr.payslip.report search
        report_recs = self.env["hr.payslip.report"].search([])
        self.assertIsNotNone(report_recs)

        # Create a validated payslip for report rendering
        payslip = self.env["hr.payslip"].create(
            {
                "name": "Report Test Payslip",
                "employee_id": self.employee.id,
                "contract_id": self.contract.id,
                "struct_id": self.structure_base.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )
        payslip.action_compute_sheet()
        payslip.action_payslip_done()

        # Payslip details report
        report_payslip_details = self.env[
            "report.hr_payroll_community.report_payslipdetails"
        ]
        vals_details = report_payslip_details._get_report_values(payslip.ids)
        self.assertIn("docs", vals_details)

        # Contribution register report
        reg = self.env.ref(
            "hr_payroll_community.contribution_register_employees"
        )
        report_contrib = self.env[
            "report.hr_payroll_community.report_contributionregister"
        ]
        data = {
            "form": {
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        }
        vals_contrib = report_contrib._get_report_values(reg.ids, data=data)
        self.assertIn("lines_data", vals_contrib)

    def test_13_access_rights_and_multicompany(self):
        """Test access rights for officer, manager, non-payroll user, and multi-company behaviour."""
        group_user = self.env.ref("base.group_user")
        group_officer = self.env.ref(
            "hr_payroll_community.group_hr_payroll_community_user"
        )
        group_manager = self.env.ref(
            "hr_payroll_community.group_hr_payroll_community_manager"
        )

        # 1. Non-payroll internal user
        non_payroll_user = self.env["res.users"].create(
            {
                "name": "Non Payroll User",
                "login": "non_payroll_user",
                "email": "non_payroll@test.com",
                "group_ids": [(6, 0, [group_user.id])],
            }
        )
        self.assertFalse(
            self.env["hr.payslip"]
            .with_user(non_payroll_user)
            .has_access("read")
        )
        self.assertFalse(
            self.env["hr.salary.rule"]
            .with_user(non_payroll_user)
            .has_access("read")
        )

        # 2. Officer user
        officer_user = self.env["res.users"].create(
            {
                "name": "Payroll Officer User",
                "login": "payroll_officer_user",
                "email": "officer@test.com",
                "group_ids": [(6, 0, [group_user.id, group_officer.id])],
            }
        )
        self.assertTrue(
            self.env["hr.payslip"].with_user(officer_user).has_access("read")
        )
        self.assertTrue(
            self.env["hr.payslip.run"]
            .with_user(officer_user)
            .has_access("read")
        )
        self.assertFalse(
            self.env["hr.payslip.report"]
            .with_user(officer_user)
            .has_access("read")
        )

        # 3. Manager user
        manager_user = self.env["res.users"].create(
            {
                "name": "Payroll Manager User",
                "login": "payroll_manager_user",
                "email": "manager@test.com",
                "group_ids": [(6, 0, [group_user.id, group_manager.id])],
            }
        )
        self.assertTrue(
            self.env["hr.payslip"].with_user(manager_user).has_access("read")
        )
        self.assertTrue(
            self.env["hr.payslip.run"]
            .with_user(manager_user)
            .has_access("read")
        )
        self.assertTrue(
            self.env["hr.payslip.report"]
            .with_user(manager_user)
            .has_access("read")
        )

        # 4. Multi-company check
        company_b = self.env["res.company"].create({"name": "Company B"})
        payslip_a = self.env["hr.payslip"].create(
            {
                "name": "Payslip Company A",
                "employee_id": self.employee.id,
                "contract_id": self.contract.id,
                "struct_id": self.structure_base.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "company_id": self.company.id,
            }
        )
        officer_company_b = self.env["res.users"].create(
            {
                "name": "Officer Company B",
                "login": "officer_b",
                "email": "officer_b@test.com",
                "company_id": company_b.id,
                "company_ids": [(6, 0, [company_b.id])],
                "group_ids": [(6, 0, [group_user.id, group_officer.id])],
            }
        )
        search_res = (
            self.env["hr.payslip"]
            .with_user(officer_company_b)
            .with_context(allowed_company_ids=[company_b.id])
            .search([("id", "=", payslip_a.id)])
        )
        self.assertEqual(len(search_res), 0)
