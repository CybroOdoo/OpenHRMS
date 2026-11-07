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
class TestHrPayslipGosi(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({
            "name": "GOSI Payslip Employee",
        })
        cls.gosi = cls.env["gosi.payslip"].create({
            "employee_id": cls.employee.id,
        })

    def test_onchange_employee_id_sets_matching_gosi_reference(self):
        payslip = self.env["hr.payslip"].new({
            "employee_id": self.employee.id,
        })

        payslip._onchange_employee_id()

        self.assertEqual(payslip.gosi_no_id, self.gosi)

    def test_onchange_employee_id_leaves_reference_empty_without_gosi(self):
        employee = self.env["hr.employee"].create({
            "name": "Employee Without GOSI",
        })
        payslip = self.env["hr.payslip"].new({
            "employee_id": employee.id,
        })

        payslip._onchange_employee_id()

        self.assertFalse(payslip.gosi_no_id)

    def test_onchange_employee_id_clears_reference_when_employee_unset(self):
        payslip = self.env["hr.payslip"].new({
            "employee_id": self.employee.id,
            "gosi_no_id": self.gosi.id,
        })

        payslip.employee_id = False
        payslip._onchange_employee_id()

        self.assertFalse(payslip.gosi_no_id)
