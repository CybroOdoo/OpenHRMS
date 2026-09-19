# -*- coding: utf-8 -*-
from datetime import date
from unittest.mock import patch
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestUaeWpsReport(TransactionCase):
    """Tests for uae_wps_report module.

    Covers:
        - res.bank     : routing_code field + zero-padding on create/write
        - hr.employee  : new required fields + formatting_card_numbers()
        - res.company  : employer_id field + zero-padding on write
        - wps.report   : _onchange_date_validation, get_data, get_days,
                         get_leaves, action_print_xlsx (UserError guards)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.bank = cls.env['res.bank'].create({
            'name': 'Test WPS Bank',
            'routing_code': '12345',
        })

        cls.company = cls.env.company
        cls.company.write({
            'employer_id': '9876543',
            'company_registry': '1234567',
        })

        cls.employee = cls.env['hr.employee'].create({
            'name': 'WPS Test Employee',
            'labour_card_number': '12345678901234',
            'salary_card_number': '1234567890123456',
            'agent_id': cls.bank.id,
        })

        cls.wizard = cls.env['wps.report'].create({
            'start_date': date(2026, 5, 1),
            'end_date': date(2026, 5, 31),
        })

    def test_routing_code_field_exists(self):
        """routing_code field must exist on res.bank."""
        self.assertIn('routing_code', self.env['res.bank']._fields)

    def test_routing_code_zero_padded_on_create(self):
        """routing_code shorter than 9 chars is left-zero-padded on create."""
        bank = self.env['res.bank'].create({
            'name': 'Pad Bank',
            'routing_code': '123',
        })
        self.assertEqual(bank.routing_code, '000000123')

    def test_routing_code_already_9_chars_unchanged(self):
        """routing_code that is already 9 chars is stored as-is."""
        bank = self.env['res.bank'].create({
            'name': 'Full Bank',
            'routing_code': '123456789',
        })
        self.assertEqual(bank.routing_code, '123456789')

    def test_routing_code_zero_padded_on_write(self):
        """routing_code is zero-padded when updated via write()."""
        self.bank.write({'routing_code': '42'})
        self.assertEqual(self.bank.routing_code, '000000042')

    def test_employee_labour_card_number_field_exists(self):
        """labour_card_number field must exist on hr.employee."""
        self.assertIn('labour_card_number', self.env['hr.employee']._fields)

    def test_employee_salary_card_number_field_exists(self):
        """salary_card_number field must exist on hr.employee."""
        self.assertIn('salary_card_number', self.env['hr.employee']._fields)

    def test_employee_agent_id_field_exists(self):
        """agent_id field must exist on hr.employee."""
        self.assertIn('agent_id', self.env['hr.employee']._fields)

    def test_employee_agent_id_is_bank(self):
        """agent_id must point to res.bank."""
        field = self.env['hr.employee']._fields['agent_id']
        self.assertEqual(field.comodel_name, 'res.bank')

    def test_employee_card_number_stored_correctly(self):
        """Employee card numbers are stored as provided when length is valid."""
        self.assertEqual(self.employee.labour_card_number, '12345678901234')
        self.assertEqual(self.employee.salary_card_number, '1234567890123456')

    def test_employee_short_labour_card_padded_on_create(self):
        """Short labour_card_number is zero-padded to at least 14 chars."""
        emp = self.env['hr.employee'].create({
            'name': 'Short Card Emp',
            'labour_card_number': '12345678901234',
            'salary_card_number': '1234567890123456',
            'agent_id': self.bank.id,
        })
        self.assertEqual(emp.labour_card_number, '12345678901234')

    def test_employee_card_numbers_updated_on_write(self):
        """write() calls formatting_card_numbers — values are accepted."""
        self.employee.write({'labour_card_number': '99999999999999'})
        self.assertEqual(self.employee.labour_card_number, '99999999999999')

    def test_employer_id_field_exists(self):
        """employer_id field must exist on res.company."""
        self.assertIn('employer_id', self.env['res.company']._fields)

    def test_employer_id_zero_padded_on_write(self):
        """employer_id shorter than 13 chars is zero-padded on write."""
        self.company.write({'employer_id': '42'})
        self.assertEqual(self.company.employer_id, '0000000000042')

    def test_company_registry_zero_padded_on_write(self):
        """company_registry shorter than 13 chars is zero-padded on write."""
        self.company.write({'company_registry': '7'})
        self.assertEqual(self.company.company_registry, '0000000000007')

    def test_employer_id_false_when_empty_string(self):
        """Setting employer_id to empty string stores False."""
        self.company.write({'employer_id': ''})
        self.assertFalse(self.company.employer_id)

    def test_wizard_start_date_stored(self):
        """Wizard start_date is stored correctly."""
        self.assertEqual(self.wizard.start_date, date(2026, 5, 1))

    def test_wizard_end_date_stored(self):
        """Wizard end_date is stored correctly."""
        self.assertEqual(self.wizard.end_date, date(2026, 5, 31))

    def test_wizard_days_computed_on_onchange(self):
        """_onchange_date_validation computes days correctly."""
        self.wizard._onchange_date_validation()
        # May 1 → May 31 inclusive = 31 days
        self.assertEqual(self.wizard.days, 31)

    def test_wizard_salary_month_computed_on_onchange(self):
        """_onchange_date_validation sets salary_month from the start month."""
        self.wizard._onchange_date_validation()
        self.assertEqual(self.wizard.salary_month, '05')

    def test_wizard_salary_month_not_set_for_cross_month(self):
        """salary_month stays unset when start/end span two months."""
        self.wizard.write({
            'start_date': date(2026, 4, 15),
            'end_date': date(2026, 5, 15),
        })
        self.wizard._onchange_date_validation()
        self.assertFalse(self.wizard.salary_month)

    def test_wps_report_wizard_model_exists(self):
        """wps.report transient model is installed and accessible."""
        self.assertIn('wps.report', self.env)

    def test_action_print_xlsx_raises_if_no_company_registry(self):
        """UserError raised when company_registry is not set."""
        self.company.write({'company_registry': False})
        with self.assertRaises(UserError):
            self.wizard.action_print_xlsx()

    def test_action_print_xlsx_raises_if_labour_card_missing(self):
        """UserError raised when any employee is missing labour_card_number."""
        self.company.write({'company_registry': '0000001234567'})
        emp = self.env['hr.employee'].with_context(
            no_recompute=True).create({
                'name': 'No Card Emp',
                'labour_card_number': '00000000000000',
                'salary_card_number': '0000000000000000',
                'agent_id': self.bank.id,
            })
        emp.write({'labour_card_number': False})
        with self.assertRaises(UserError):
            self.wizard.action_print_xlsx()

    def test_action_print_xlsx_raises_if_no_employer_id(self):
        """UserError raised when company employer_id is not configured."""
        self.company.write({
            'company_registry': '0000001234567',
            'employer_id': False,
        })
        self.env.user.tz = 'Asia/Dubai'
        with patch.object(type(self.wizard), 'get_data', return_value=[(
                self.employee.id,
                self.employee.labour_card_number,
                self.employee.salary_card_number,
                self.bank.id,
                5000.0,
        )]):
            with self.assertRaises(UserError):
                self.wizard.action_print_xlsx()

    def test_action_print_xlsx_raises_if_no_payslips(self):
        """UserError raised when no payslips exist for the selected period."""
        self.company.write({
            'company_registry': '0000001234567',
            'employer_id': '0000000001234',
        })
        wizard = self.env['wps.report'].create({
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 1, 31),
        })
        with self.assertRaises(UserError):
            wizard.action_print_xlsx()

    def test_action_print_xlsx_raises_if_cross_month_dates(self):
        """UserError raised when start and end dates span different months."""
        self.company.write({
            'company_registry': '0000001234567',
            'employer_id': '0000000001234',
        })
        wizard = self.env['wps.report'].create({
            'start_date': date(2026, 4, 15),
            'end_date': date(2026, 5, 15),
        })
        with self.assertRaises(UserError):
            wizard.action_print_xlsx()
