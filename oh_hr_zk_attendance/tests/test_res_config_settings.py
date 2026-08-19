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

from datetime import timedelta

from odoo import fields

from .common import OhHrZkAttendanceCommon


class TestResConfigSettings(OhHrZkAttendanceCommon):
    def test_set_values_enables_attendance_cron(self):
        settings = self.env["res.config.settings"].create({
            "schedule_attendance_downloads": True,
            "schedule_time_interval": 4,
            "schedule_time_period": "hours",
        })
        before = fields.Datetime.now()
        settings.set_values()
        after = fields.Datetime.now()

        self.cron.invalidate_recordset()
        self.assertTrue(self.cron.active)
        self.assertEqual(self.cron.interval_type, "hours")
        self.assertEqual(self.cron.interval_number, 4)
        expected_delta = self.cron.nextcall - before
        self.assertGreaterEqual(expected_delta, timedelta(hours=4))
        self.assertLess(expected_delta, timedelta(hours=4, seconds=2))

    def test_set_values_disables_attendance_cron(self):
        self.cron.active = True
        settings = self.env["res.config.settings"].create({
            "schedule_attendance_downloads": False,
        })

        settings.set_values()

        self.cron.invalidate_recordset()
        self.assertFalse(self.cron.active)
