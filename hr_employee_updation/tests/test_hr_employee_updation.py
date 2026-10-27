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
from datetime import timedelta
from odoo import fields
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestHrEmployeeUpdation(TransactionCase):
    """Test suite for hr_employee_updation module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.contract_expiration_notice_period = 30

        cls.relation_spouse = cls.env.ref('hr_employee_updation.employee_relationship')
        cls.relation_child = cls.env['hr.employee.relation'].create({'name': 'Child'})

        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Jane Doe',
            'work_email': 'jane.doe@example.com',
            'identification_id': 'ID-99999',
            'passport_id': 'PASS-88888',
        })

    def test_01_hr_version_notice_days(self):
        """Test notice days computation on hr.version."""
        version = self.employee.version_ids[:1]
        if not version:
            version = self.env['hr.version'].create({
                'employee_id': self.employee.id,
                'date_version': fields.Date.today() - timedelta(days=1),
                'contract_date_start': fields.Date.today() - timedelta(days=1),
                'company_id': self.company.id,
            })
        self.assertEqual(version.notice_days, 30)

    def test_02_joining_date_computation(self):
        """Test joining date computation from contract versions."""
        earlier_date = fields.Date.today() - timedelta(days=120)
        self.env['hr.version'].create({
            'employee_id': self.employee.id,
            'date_version': earlier_date,
            'contract_date_start': earlier_date,
            'company_id': self.company.id,
        })

        self.employee._compute_joining_date()
        self.assertEqual(self.employee.joining_date, earlier_date)

    def test_03_spouse_onchange_and_family_info(self):
        """Test family info creation and spouse onchange behavior."""
        child_member = self.env['hr.employee.family'].create({
            'employee_id': self.employee.id,
            'relation_id': self.relation_child.id,
            'member_name': 'Tommy Doe',
        })
        self.assertIn(child_member, self.employee.family_info_ids)

        # Trigger spouse onchange
        self.employee.spouse_complete_name = 'John Doe'
        self.employee.spouse_birthdate = fields.Date.from_string('1990-01-01')
        self.employee._onchange_spouse_complete_name()

        spouse_line = self.employee.family_info_ids.filtered(
            lambda f: f.relation_id == self.relation_spouse
        )
        self.assertTrue(spouse_line)
        self.assertEqual(spouse_line[0].member_name, 'John Doe')

        # Verify child is preserved
        self.assertIn(child_member, self.employee.family_info_ids)

        # Update spouse name onchange
        self.employee.spouse_complete_name = 'Johnathan Doe'
        self.employee._onchange_spouse_complete_name()
        self.assertEqual(spouse_line[0].member_name, 'Johnathan Doe')

    def test_04_automated_expiry_mail_reminder(self):
        """Test automated cron ID and passport expiry reminders."""
        today = fields.Date.today()
        id_days = 14
        passport_days = 180

        self.env['ir.config_parameter'].sudo().set_int(
            'hr_employee_updation.id_expiry_days', id_days
        )
        self.env['ir.config_parameter'].sudo().set_int(
            'hr_employee_updation.passport_expiry_days', passport_days
        )

        self.employee.write({
            'id_expiry_date': today + timedelta(days=id_days),
            'passport_expiration_date': today + timedelta(days=passport_days),
        })

        initial_mail_count = self.env['mail.mail'].search_count([])
        self.employee.expiry_mail_reminder()
        new_mail_count = self.env['mail.mail'].search_count([])

        self.assertEqual(new_mail_count, initial_mail_count + 2)

    def test_05_manual_reminders(self):
        """Test manual ID and passport reminder actions."""
        self.employee.write({
            'id_expiry_date': fields.Date.today() + timedelta(days=10),
            'passport_expiration_date': fields.Date.today() + timedelta(days=45),
        })

        initial_mail_count = self.env['mail.mail'].search_count([])
        self.employee.action_send_manual_reminder_id()
        self.employee.action_send_manual_reminder_pass()
        new_mail_count = self.env['mail.mail'].search_count([])

        self.assertEqual(new_mail_count, initial_mail_count + 2)

    def test_06_res_config_settings(self):
        """Test configuration settings for ID and Passport lead days."""
        settings = self.env['res.config.settings'].create({
            'id_expiry_days': 20,
            'passport_expiry_days': 90,
        })
        settings.execute()

        id_days = self.env['ir.config_parameter'].sudo().get_int('hr_employee_updation.id_expiry_days')
        passport_days = self.env['ir.config_parameter'].sudo().get_int('hr_employee_updation.passport_expiry_days')
        self.assertEqual(id_days, 20)
        self.assertEqual(passport_days, 90)
