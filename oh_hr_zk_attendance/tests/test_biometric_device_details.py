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

from unittest.mock import patch

from odoo.addons.oh_hr_zk_attendance.models import biometric_device_details as biometric_module

from .common import FakeConnection, FakeUser, FakeZK, OhHrZkAttendanceCommon


class TestBiometricDeviceDetails(OhHrZkAttendanceCommon):
    def test_device_connect_returns_connection(self):
        zk = FakeZK()

        self.assertTrue(self.device.device_connect(zk))

    def test_action_test_connection_returns_notification(self):
        with patch.object(biometric_module, "ZK", FakeZK):
            action = self.device.action_test_connection()

        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "success")

    def test_action_set_timezone_updates_connected_device(self):
        fake_connection = FakeConnection()

        with patch.object(type(self.device), "device_connect", autospec=True, return_value=fake_connection), \
             patch.object(biometric_module, "ZK", FakeZK):
            action = self.device.with_context(tz="Asia/Kolkata").action_set_timezone()

        self.assertEqual(action["tag"], "display_notification")
        self.assertTrue(fake_connection.set_time_value)

    def test_get_all_users_creates_employee_records(self):
        fake_connection = FakeConnection(users=[FakeUser(1, "1001", "New Employee")])

        with patch.object(type(self.device), "device_connect", autospec=True, return_value=fake_connection), \
             patch.object(biometric_module, "ZK", FakeZK):
            self.device.get_all_users()

        employee = self.env["hr.employee"].search([
            ("device_id_num", "=", "1001"),
            ("device_id", "=", self.device.id),
        ])
        self.assertEqual(employee.name, "New Employee")

    def test_schedule_attendance_restarts_live_capture_flow(self):
        self.device.write({"is_live_capture": True})

        with patch.object(type(self.device), "action_stop_live_capture", autospec=True) as stop_mock, \
             patch.object(type(self.device), "action_download_attendance", autospec=True) as download_mock, \
             patch.object(type(self.device), "action_live_capture", autospec=True) as live_mock:
            self.device.schedule_attendance()

        stop_mock.assert_called_once()
        download_mock.assert_called_once()
        live_mock.assert_called_once()

    def test_delete_user_clears_employee_biometric_fields(self):
        self.employee.write({
            "device_id": self.device.id,
            "device_id_num": "1002",
            "fingerprint_ids": [(0, 0, {
                "finger_id": "1",
                "filename": "employee-a-finger-1",
            })],
        })
        fake_connection = FakeConnection()

        with patch.object(type(self.device), "device_connect", autospec=True, return_value=fake_connection), \
             patch.object(biometric_module, "ZK", FakeZK):
            self.device.delete_user(self.employee.id, "device_only")

        self.assertFalse(self.employee.device_id)
        self.assertFalse(self.employee.device_id_num)
        self.assertFalse(self.employee.fingerprint_ids)

    def test_update_user_returns_success_action(self):
        self.employee.write({
            "device_id": self.device.id,
            "device_id_num": "1003",
        })
        fake_connection = FakeConnection(users=[FakeUser(4, "1003", "Employee A")])

        with patch.object(type(self.device), "device_connect", autospec=True, return_value=fake_connection), \
             patch.object(biometric_module, "ZK", FakeZK):
            action = self.device.update_user(self.employee.id)

        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["message"], "Successfully Updated User")
