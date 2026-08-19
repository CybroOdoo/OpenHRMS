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


class TestDailyAttendance(OhHrZkAttendanceCommon):
    def test_daily_attendance_view_exposes_machine_attendance_rows(self):
        machine_attendance = self.env["zk.machine.attendance"].create({
            "employee_id": self.employee.id,
            "check_in": "2026-05-04 09:00:00",
            "check_out": "2026-05-04 18:00:00",
            "device_id_num": "1001",
            "attendance_type": "1",
            "punch_type": "0",
            "punching_time": "2026-05-04 09:00:00",
            "address_id": self.address.id,
        })

        daily_attendance = self.env["daily.attendance"].search([
            ("employee_id", "=", self.employee.id),
            ("punching_time", "=", "2026-05-04 09:00:00"),
        ])

        self.assertTrue(daily_attendance)
        self.assertEqual(daily_attendance.employee_id, self.employee)
        self.assertEqual(daily_attendance.address_id, self.address)
        self.assertEqual(daily_attendance.attendance_type, machine_attendance.attendance_type)
