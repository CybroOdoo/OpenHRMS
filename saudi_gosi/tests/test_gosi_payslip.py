# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify it under the terms of the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestGosiPayslip(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({
            "name": "GOSI Employee",
        })

    def test_create_assigns_sequence_when_name_is_missing(self):
        gosi = self.env["gosi.payslip"].create({
            "employee_id": self.employee.id,
        })

        self.assertTrue(gosi.name)
        self.assertNotEqual(gosi.name, "New")

    def test_create_keeps_explicit_name(self):
        gosi = self.env["gosi.payslip"].create({
            "employee_id": self.employee.id,
            "name": "MANUAL-GOSI",
        })

        self.assertEqual(gosi.name, "MANUAL-GOSI")

    def test_create_accepts_multiple_values(self):
        employees = self.env["hr.employee"].create([
            {"name": "GOSI Employee A"},
            {"name": "GOSI Employee B"},
        ])

        gosi_records = self.env["gosi.payslip"].create([
            {"employee_id": employees[0].id},
            {"employee_id": employees[1].id},
        ])

        self.assertEqual(len(gosi_records), 2)
        self.assertTrue(
            all(record.name and record.name != "New" for record in gosi_records)
        )
