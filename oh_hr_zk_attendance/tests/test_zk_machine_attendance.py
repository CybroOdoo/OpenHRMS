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


class TestZkMachineAttendance(OhHrZkAttendanceCommon):
    def test_overlapping_machine_attendance_is_allowed(self):
        first_attendance = self.env["zk.machine.attendance"].create({
            "employee_id": self.employee.id,
            "check_in": "2026-05-04 09:00:00",
            "check_out": "2026-05-04 12:00:00",
            "punching_time": "2026-05-04 09:00:00",
            "device_id_num": "1001",
        })
        second_attendance = self.env["zk.machine.attendance"].create({
            "employee_id": self.employee.id,
            "check_in": "2026-05-04 11:00:00",
            "check_out": "2026-05-04 13:00:00",
            "punching_time": "2026-05-04 11:00:00",
            "device_id_num": "1001",
        })

        self.assertTrue(first_attendance)
        self.assertTrue(second_attendance)

    def test_company_defaults_to_current_company(self):
        attendance = self.env["zk.machine.attendance"].create({
            "employee_id": self.employee.id,
            "check_in": "2026-05-04 09:00:00",
            "punching_time": "2026-05-04 09:00:00",
            "device_id_num": "1001",
        })

        self.assertEqual(attendance.company_id, self.env.company)
