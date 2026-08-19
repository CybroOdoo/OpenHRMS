# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify it under the terms of the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from .common import OhHrZkAttendanceCommon


class TestFingerprintTemplates(OhHrZkAttendanceCommon):
    def test_fingerprint_template_is_linked_to_employee(self):
        fingerprint = self.env["fingerprint.templates"].create({
            "employee_id": self.employee.id,
            "finger_id": "2",
            "filename": "employee-a-finger-2",
            "finger_template": b"ZmFrZS10ZW1wbGF0ZQ==",
        })

        self.assertEqual(fingerprint.employee_id, self.employee)
        self.assertEqual(fingerprint.finger_id, "2")
        self.assertIn(fingerprint, self.employee.fingerprint_ids)
