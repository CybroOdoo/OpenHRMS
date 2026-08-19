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

from types import SimpleNamespace

from odoo.tests.common import TransactionCase


class OhHrZkAttendanceCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address = cls.env["res.partner"].create({"name": "HQ"})
        cls.device = cls.env["biometric.device.details"].create({
            "name": "Device A",
            "device_ip": "192.168.1.10",
            "port_number": 4370,
            "address_id": cls.address.id,
        })
        cls.employee = cls.env["hr.employee"].create({
            "name": "Employee A",
            "company_id": cls.env.company.id,
        })
        cls.other_employee = cls.env["hr.employee"].create({
            "name": "Employee B",
            "company_id": cls.env.company.id,
        })
        cls.cron = cls.env.ref("oh_hr_zk_attendance.ir_cron_schedule_attendance_action")


class FakeUser:
    def __init__(self, uid, user_id, name):
        self.uid = uid
        self.user_id = user_id
        self.name = name


class FakeConnection:
    def __init__(self, users=None):
        self.users = users or []
        self.set_time_value = None
        self.enabled = False
        self.disabled = False
        self.end_live_capture = False

    def get_users(self):
        return self.users

    def enable_device(self):
        self.enabled = True

    def disable_device(self):
        self.disabled = True

    def set_time(self, value):
        self.set_time_value = value

    def set_user(self, *args):
        self.set_user_args = args

    def delete_user(self, uid=None, user_id=None):
        self.deleted_user_id = user_id


class FakeZK:
    def __init__(self, *args, **kwargs):
        self.connected = True
        self.voice_tested = None

    def connect(self):
        return self.connected

    def test_voice(self, index=0):
        self.voice_tested = index


def make_action(action_type):
    return {"type": action_type}


def make_notification():
    return {"type": "ir.actions.client", "tag": "display_notification"}


def make_reload():
    return {"type": "ir.actions.client", "tag": "reload"}


def make_user(uid, user_id, name):
    return SimpleNamespace(uid=uid, user_id=user_id, name=name)
