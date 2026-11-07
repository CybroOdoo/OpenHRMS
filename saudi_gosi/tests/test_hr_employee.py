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

from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrEmployeeGosi(TransactionCase):

    def _create_employee_with_age(self, years):
        return self.env["hr.employee"].create({
            "name": "GOSI Age Employee",
            "birthday": date.today() - timedelta(days=years * 365),
        })

    def test_compute_age_marks_employee_between_18_and_60_as_eligible(self):
        employee = self._create_employee_with_age(30)

        employee._compute_age()

        self.assertEqual(employee.age, "30")
        self.assertTrue(employee.limit)

    def test_compute_age_marks_employee_below_18_as_not_eligible(self):
        employee = self._create_employee_with_age(17)

        employee._compute_age()

        self.assertEqual(employee.age, "17")
        self.assertFalse(employee.limit)

    def test_compute_age_marks_employee_above_60_as_not_eligible(self):
        employee = self._create_employee_with_age(61)

        employee._compute_age()

        self.assertEqual(employee.age, "61")
        self.assertFalse(employee.limit)

    def test_compute_age_without_birthday_resets_age_and_eligibility(self):
        employee = self.env["hr.employee"].create({
            "name": "GOSI Employee Without Birthday",
        })

        employee._compute_age()

        self.assertEqual(employee.age, "0")
        self.assertFalse(employee.limit)
