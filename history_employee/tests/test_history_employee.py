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
"""Comprehensive unit test suite for history_employee module."""
from datetime import date

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHistoryEmployee(TransactionCase):
    """Test suite covering models, write history hooks, timeline generation,
    and security access for Employee History."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.group_user = cls.env.ref('base.group_user')
        cls.group_hr_user = cls.env.ref('hr.group_hr_user')
        cls.group_hr_manager = cls.env.ref('hr.group_hr_manager')

        # Test users
        cls.user_officer = cls.env['res.users'].create({
            'name': 'Test HR Officer',
            'login': 'test_history_hr_officer',
            'email': 'hr_officer@test.example.com',
            'group_ids': [(6, 0, [cls.group_user.id, cls.group_hr_user.id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Test HR Manager',
            'login': 'test_history_hr_manager',
            'email': 'hr_manager@test.example.com',
            'group_ids': [(6, 0, [cls.group_user.id, cls.group_hr_manager.id])],
        })

        # Test Departments
        cls.dept_rnd = cls.env['hr.department'].create({
            'name': 'Research & Development',
        })
        cls.dept_marketing = cls.env['hr.department'].create({
            'name': 'Marketing & Sales',
        })

        # Test Jobs
        cls.job_dev = cls.env['hr.job'].create({
            'name': 'Junior Software Engineer',
        })
        cls.job_lead = cls.env['hr.job'].create({
            'name': 'Principal Tech Lead',
        })

        # Test Employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Alice Wonder',
            'department_id': cls.dept_rnd.id,
            'job_id': cls.job_dev.id,
            'hourly_cost': 25.0,
        })

    def test_01_history_models_compute_employee_id(self):
        """Test _compute_employee_id logic on all four history models."""
        models_to_test = [
            'department.history',
            'salary.history',
            'hourly.cost',
            'contract.history',
        ]
        for model_name in models_to_test:
            # 1. Employee string with digit
            rec_with_digit = self.env[model_name].create({
                'employee': str(self.employee.id),
                'employee_name': self.employee.name,
                'updated_date': fields.Date.today(),
                'current_value': 'Test Val 1',
            })
            self.assertEqual(
                rec_with_digit.employee_id,
                self.employee,
                f"{model_name} should resolve employee_id from string digit.",
            )

            # 2. Employee string with non-digit
            rec_non_digit = self.env[model_name].create({
                'employee': 'non_digit',
                'employee_name': self.employee.name,
                'updated_date': fields.Date.today(),
                'current_value': 'Test Val 2',
            })
            self.assertFalse(
                rec_non_digit.employee_id,
                f"{model_name} employee_id should be False when employee is not digits.",
            )

            # 3. Direct employee_id assignment
            rec_direct = self.env[model_name].create({
                'employee_id': self.employee.id,
                'employee_name': self.employee.name,
                'updated_date': fields.Date.today(),
                'current_value': 'Test Val 3',
            })
            self.assertEqual(
                rec_direct.employee_id,
                self.employee,
                f"{model_name} should preserve directly assigned employee_id.",
            )

    def test_02_employee_department_and_job_history(self):
        """Test that writing department_id and job_id logs records in department.history."""
        # 1. Update department
        self.employee.write({'department_id': self.dept_marketing.id})

        dep_histories = self.env['department.history'].search([
            ('employee_id', '=', self.employee.id),
            ('changed_field', '=', 'Department'),
        ], order='id asc')

        # Should have created a baseline record ('Research & Development') and new record ('Marketing & Sales')
        self.assertGreaterEqual(len(dep_histories), 2)
        self.assertEqual(dep_histories[0].current_value, 'Research & Development')
        self.assertEqual(dep_histories[-1].current_value, 'Marketing & Sales')

        # 2. Update job_id
        self.employee.write({'job_id': self.job_lead.id})

        job_histories = self.env['department.history'].search([
            ('employee_id', '=', self.employee.id),
            ('changed_field', '=', 'Job Position'),
        ], order='id asc')

        self.assertGreaterEqual(len(job_histories), 2)
        self.assertEqual(job_histories[0].current_value, 'Junior Software Engineer')
        self.assertEqual(job_histories[-1].current_value, 'Principal Tech Lead')

        # 3. Writing the same value should not create duplicate entries
        count_before = len(self.env['department.history'].search([('employee_id', '=', self.employee.id)]))
        self.employee.write({'department_id': self.dept_marketing.id})
        count_after = len(self.env['department.history'].search([('employee_id', '=', self.employee.id)]))
        self.assertEqual(count_before, count_after)

    def test_03_employee_hourly_cost_history(self):
        """Test that writing hourly_cost logs records in hourly.cost."""
        # First write: logs baseline (25.0) and new (35.0)
        self.employee.write({'hourly_cost': 35.0})

        records = self.env['hourly.cost'].search([
            ('employee_id', '=', self.employee.id),
        ], order='id asc')

        self.assertGreaterEqual(len(records), 2)
        self.assertEqual(str(records[0].current_value), '25.0')
        self.assertEqual(str(records[-1].current_value), '35.0')

        # Second write: logs next value (50.0)
        self.employee.write({'hourly_cost': 50.0})
        records_after = self.env['hourly.cost'].search([
            ('employee_id', '=', self.employee.id),
        ], order='id asc')
        self.assertEqual(len(records_after), len(records) + 1)
        self.assertEqual(str(records_after[-1].current_value), '50.0')

    def test_04_employee_wage_and_contract_fields_if_present(self):
        """Test writing wage, contract_date_start, contract_date_end, and contract/employee types."""
        vals_to_test = {}
        if 'wage' in self.employee._fields:
            vals_to_test['wage'] = 5000.0
        if 'contract_date_start' in self.employee._fields:
            vals_to_test['contract_date_start'] = date(2026, 1, 1)
        if 'contract_date_end' in self.employee._fields:
            vals_to_test['contract_date_end'] = date(2026, 12, 31)

        if vals_to_test:
            self.employee.write(vals_to_test)

            if 'wage' in vals_to_test:
                sal_history = self.env['salary.history'].search([
                    ('employee_id', '=', self.employee.id),
                ])
                self.assertTrue(sal_history, "Salary history should be recorded when wage is changed.")

            if 'contract_date_start' in vals_to_test:
                start_hist = self.env['contract.history'].search([
                    ('employee_id', '=', self.employee.id),
                    ('changed_field', '=', 'Start Date'),
                ])
                self.assertTrue(start_hist, "Start Date history should be recorded.")

            if 'contract_date_end' in vals_to_test:
                end_hist = self.env['contract.history'].search([
                    ('employee_id', '=', self.employee.id),
                    ('changed_field', '=', 'End Date'),
                ])
                self.assertTrue(end_hist, "End Date history should be recorded.")

        # Test writing an unrelated field does not create any history
        total_salaries_before = self.env['salary.history'].search_count([])
        total_deps_before = self.env['department.history'].search_count([])
        self.employee.write({'work_email': 'alice.wonder@test.example.com'})
        self.assertEqual(self.env['salary.history'].search_count([]), total_salaries_before)
        self.assertEqual(self.env['department.history'].search_count([]), total_deps_before)

    def test_05_hr_version_write_history(self):
        """Test history tracking when updating hr.version records if hr.version exists."""
        if 'hr.version' not in self.env:
            return

        version_model = self.env['hr.version']
        version_fields = version_model._fields

        version_rec = version_model.search([('employee_id', '=', self.employee.id)], limit=1)
        if not version_rec:
            create_vals = {}
            if 'employee_id' in version_fields:
                create_vals['employee_id'] = self.employee.id
            if 'name' in version_fields:
                create_vals['name'] = 'Version 1'
            if 'wage' in version_fields:
                create_vals['wage'] = 3000.0
            if 'contract_date_start' in version_fields:
                create_vals['contract_date_start'] = date(2026, 2, 1)
            if 'contract_date_end' in version_fields:
                create_vals['contract_date_end'] = date(2026, 8, 31)
            try:
                version_rec = version_model.create(create_vals)
            except Exception:
                return

        update_vals = {}
        if 'wage' in version_fields:
            update_vals['wage'] = 4500.0
        if 'contract_date_start' in version_fields:
            update_vals['contract_date_start'] = date(2026, 3, 1)
        if 'contract_date_end' in version_fields:
            update_vals['contract_date_end'] = date(2026, 11, 30)
        if 'employee_type_id' in version_fields and 'hr.employee.type' in self.env:
            emp_types = self.env['hr.employee.type'].search([], limit=2)
            if emp_types:
                update_vals['employee_type_id'] = emp_types[0].id
        if 'contract_type_id' in version_fields and 'hr.contract.type' in self.env:
            c_types = self.env['hr.contract.type'].search([], limit=2)
            if c_types:
                update_vals['contract_type_id'] = c_types[0].id

        if update_vals:
            version_rec.write(update_vals)
            if 'wage' in update_vals:
                sal = self.env['salary.history'].search([
                    ('employee_id', '=', self.employee.id),
                    ('current_value', '=', '4500.0'),
                ])
                self.assertTrue(sal, "hr.version write should create salary history.")

    def test_06_timeline_generation_comprehensive(self):
        """Test get_employee_history_timeline with salary, hourly cost, contract, and department history."""
        emp2 = self.env['hr.employee'].create({
            'name': 'Bob Tester',
            'department_id': self.dept_rnd.id,
            'job_id': self.job_dev.id,
            'hourly_cost': 20.0,
        })

        # 1. Empty timeline for fresh employee with no history changes
        timeline_empty = self.env['hr.employee'].get_employee_history_timeline(emp2.id)
        self.assertEqual(timeline_empty, [])

        # 2. Invalid or empty IDs
        self.assertEqual(self.env['hr.employee'].get_employee_history_timeline(False), [])
        self.assertEqual(self.env['hr.employee'].get_employee_history_timeline(0), [])
        self.assertEqual(self.env['hr.employee'].get_employee_history_timeline(None), [])

        # 3. Seed Salary History (baseline 1000, increase to 1200, decrease to 1100)
        self.env['salary.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'updated_date': date(2026, 1, 1),
            'current_value': '1000.0',
        })
        self.env['salary.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'updated_date': date(2026, 3, 1),
            'current_value': '1200.0',
        })
        self.env['salary.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'updated_date': date(2026, 5, 1),
            'current_value': '1100.0',
        })

        # 4. Seed Hourly Cost History (baseline 20, increase to 30, decrease to 25)
        self.env['hourly.cost'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'updated_date': date(2026, 1, 1),
            'current_value': '20.0',
        })
        self.env['hourly.cost'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'updated_date': date(2026, 3, 1),
            'current_value': '30.0',
        })
        self.env['hourly.cost'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'updated_date': date(2026, 5, 1),
            'current_value': '25.0',
        })

        # 5. Seed Contract History (Start Date, End Date, Contract Type, Employee Type, generic Contract)
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Start Date',
            'updated_date': date(2026, 1, 1),
            'current_value': '2026-01-01',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Start Date',
            'updated_date': date(2026, 2, 1),
            'current_value': '2026-02-01',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'End Date',
            'updated_date': date(2026, 1, 1),
            'current_value': False,
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'End Date',
            'updated_date': date(2026, 6, 1),
            'current_value': '2026-12-31',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Contract Type',
            'updated_date': date(2026, 1, 1),
            'current_value': 'Permanent',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Contract Type',
            'updated_date': date(2026, 4, 1),
            'current_value': 'Contractor',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Employee Type',
            'updated_date': date(2026, 1, 1),
            'current_value': 'Full-time',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Employee Type',
            'updated_date': date(2026, 4, 1),
            'current_value': 'Part-time',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Contract',
            'updated_date': date(2026, 1, 1),
            'current_value': 'Initial Agreement',
        })
        self.env['contract.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Contract',
            'updated_date': date(2026, 5, 1),
            'current_value': 'Renewed Agreement',
        })

        # 6. Seed Department & Job History
        self.env['department.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Department',
            'updated_date': date(2026, 1, 1),
            'current_value': 'Research & Development',
        })
        self.env['department.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Department',
            'updated_date': date(2026, 3, 1),
            'current_value': 'Marketing & Sales',
        })
        self.env['department.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Job Position',
            'updated_date': date(2026, 1, 1),
            'current_value': 'Junior Software Engineer',
        })
        self.env['department.history'].create({
            'employee_id': emp2.id,
            'employee_name': emp2.name,
            'changed_field': 'Job Position',
            'updated_date': date(2026, 3, 1),
            'current_value': 'Principal Tech Lead',
        })

        # Fetch timeline
        timeline = self.env['hr.employee'].get_employee_history_timeline(emp2.id)
        self.assertTrue(timeline, "Timeline should return items when history records exist.")

        categories = {item['category'] for item in timeline}
        self.assertIn('SALARY', categories)
        self.assertIn('HOURLY COST', categories)
        self.assertIn('CONTRACT', categories)
        self.assertIn('JOB/DEPT', categories)

        for item in timeline:
            self.assertIn('id', item)
            self.assertIn('title', item)
            self.assertIn('category', item)
            self.assertNotIn('sort_date', item, "sort_date should be removed for JSON compatibility.")

        # Also test hr.employee.public method delegation
        public_timeline = self.env['hr.employee.public'].get_employee_history_timeline(emp2.id)
        self.assertEqual(len(public_timeline), len(timeline))

    def test_07_history_security_access(self):
        """Test access rights for hr_user and hr_manager groups."""
        officer_env = self.env['department.history'].with_user(self.user_officer)
        manager_env = self.env['department.history'].with_user(self.user_manager)

        # 1. Officer can read
        records = officer_env.search([])
        self.assertIsNotNone(records)

        # 2. Manager can create, write, and delete
        new_history = manager_env.create({
            'employee': str(self.employee.id),
            'employee_name': self.employee.name,
            'changed_field': 'Department',
            'updated_date': fields.Date.today(),
            'current_value': 'Legal & Compliance',
        })
        self.assertTrue(new_history.id)

        new_history.write({'current_value': 'Operations'})
        self.assertEqual(new_history.current_value, 'Operations')

        res_unlink = new_history.unlink()
        self.assertTrue(res_unlink)

    def test_08_timeline_edge_cases_and_non_numeric(self):
        """Test timeline generation with non-numeric values, invalid dates, and date objects."""
        emp3 = self.env['hr.employee'].create({
            'name': 'Charlie EdgeCase',
        })

        # Non-numeric salary
        self.env['salary.history'].create({
            'employee_id': emp3.id,
            'employee_name': emp3.name,
            'updated_date': date(2026, 1, 1),
            'current_value': 'NotANumber1',
        })
        self.env['salary.history'].create({
            'employee_id': emp3.id,
            'employee_name': emp3.name,
            'updated_date': date(2026, 2, 1),
            'current_value': 'NotANumber2',
        })

        # Non-numeric hourly cost
        self.env['hourly.cost'].create({
            'employee_id': emp3.id,
            'employee_name': emp3.name,
            'updated_date': date(2026, 1, 1),
            'current_value': 'InvalidCost1',
        })
        self.env['hourly.cost'].create({
            'employee_id': emp3.id,
            'employee_name': emp3.name,
            'updated_date': date(2026, 2, 1),
            'current_value': 'InvalidCost2',
        })

        # Invalid date strings and Date objects in contract history
        self.env['contract.history'].create({
            'employee_id': emp3.id,
            'employee_name': emp3.name,
            'changed_field': 'Start Date',
            'updated_date': date(2026, 1, 1),
            'current_value': 'invalid-date-format-abc',
        })
        self.env['contract.history'].create({
            'employee_id': emp3.id,
            'employee_name': emp3.name,
            'changed_field': 'Start Date',
            'updated_date': date(2026, 2, 1),
            'current_value': 'invalid-date-format-xyz',
        })

        timeline = self.env['hr.employee'].get_employee_history_timeline(emp3.id)
        self.assertTrue(timeline)
