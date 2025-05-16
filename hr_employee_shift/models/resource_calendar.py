# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import math
from pytz import utc
from collections import namedtuple
from datetime import datetime, time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class ResourceCalendar(models.Model):
    """Inherits from the 'resource.calendar' model to extend its functionality
       for managing employee attendance and working hours."""
    _inherit = 'resource.calendar'
    _interval_obj = namedtuple('Interval',
                               ('start_datetime', 'end_datetime', 'data'))

    def _get_default_attendance_ids(self):
        """It sets default attendance times for weekdays in an Odoo model. It
        populates attendance records for Monday to Friday mornings with specific
        day, start, and end times. Other fields include color, department relation,
        and sequence number with a default value of 1."""
        return [
            (0, 0,
             {'name': _('Monday Morning'), 'dayofweek': '0', 'hour_from': 8,
              'hour_to': 12}),
            (0, 0,
             {'name': _('Tuesday Morning'), 'dayofweek': '1', 'hour_from': 8,
              'hour_to': 12}),
            (0, 0,
             {'name': _('Wednesday Morning'), 'dayofweek': '2', 'hour_from': 8,
              'hour_to': 12}),
            (0, 0,
             {'name': _('Thursday Morning'), 'dayofweek': '3', 'hour_from': 8,
              'hour_to': 12}),
            (0, 0,
             {'name': _('Friday Morning'), 'dayofweek': '4', 'hour_from': 8,
              'hour_to': 12}),
        ]

    color = fields.Integer(string='Color Index', help="Color index for each calender")
    hr_department = fields.Many2one('hr.department', string="Department",
                                    required=True, help="Department of employee")
    sequence = fields.Integer(string="Sequence", required=True, default=1,
                              help="Sequence of the calender")
    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Working Time',
        copy=True, default=_get_default_attendance_ids, help="Attendance details from calender")

    @api.constrains('sequence')
    def validate_seq(self):
        """Ensure unique sequence within the same department and company.
        Raises a ValidationError if there is more than one record with the same sequence
        in the same department and company."""
        if self.hr_department.id:
            record = self.env['resource.calendar'].search(
                [('hr_department', '=', self.hr_department.id),
                 ('sequence', '=', self.sequence),
                 ('company_id', '=', self.company_id.id)
                 ])
            if len(record) > 1:
                raise ValidationError(
                    "One record with same sequence is already active."
                    "You can't activate more than one record  at a time")

    def string_to_datetime(self, value):
        """ Convert the given string value to a datetime in UTC. """
        return utc.localize(fields.Datetime.from_string(value))

    def float_to_time(self, hours):
        """ Convert a number of hours into a time object. """
        if hours == 24.0:
            return time.max
        fractional, integral = math.modf(hours)
        return time(int(integral),
                    int(float_round(60 * fractional, precision_digits=0)), 0)

    def _interval_new(self, start_datetime, end_datetime, kw=None):
        """ Create a new interval object with start and end datetime,
        and optional data.
        :param kw: Optional dictionary to include additional data like attendances and leaves.
                   Defaults to an empty dictionary if None is provided.
        :return: An instance of `_interval_obj` namedtuple with the provided start and end datetime,
                 and the data dictionary."""
        kw = kw if kw is not None else dict()
        kw.setdefault('attendances', self.env['resource.calendar.attendance'])
        kw.setdefault('leaves', self.env['resource.calendar.leaves'])
        return self._interval_obj(start_datetime, end_datetime, kw)

    def _get_day_work_intervals(self, day_date, start_time=None, end_time=None,
                                compute_leaves=False,
                                resource_id=None):
        """ Calculate working intervals for a given day, optionally filtering
        by start/end times and leaves.
        :return: A list of interval objects representing working periods within
                 the specified constraints."""
        self.ensure_one()
        if not start_time:
            start_time = datetime.time.min
        if not end_time:
            end_time = datetime.time.max

        working_intervals = [att_interval for att_interval in
                             self._iter_day_attendance_intervals(day_date,
                                                                 start_time,
                                                                 end_time)]
        if compute_leaves:
            leaves = self._get_leave_intervals(
                resource_id=resource_id,
                start_datetime=datetime.datetime.combine(day_date, start_time),
                end_datetime=datetime.datetime.combine(day_date, end_time))
            working_intervals = [
                sub_interval
                for interval in working_intervals
                for sub_interval in self._leave_intervals(interval, leaves)]
        return [self._interval_new(
            self.string_to_datetime(interval[0]),
            self.string_to_datetime(interval[1]),
            interval[2]) for interval in working_intervals]

    def _get_day_attendances(self, day_date, start_time, end_time):
        """ Given a day date, return matching attendances. Those can be limited
        by starting and ending time objects. """
        self.ensure_one()
        weekday = day_date.weekday()
        attendances = self.env['resource.calendar.attendance']
        for attendance in self.attendance_ids.filtered(
                lambda att:
                int(att.dayofweek) == weekday and
                not (att.date_from and fields.Date.from_string(
                    att.date_from) > day_date) and
                not (att.date_to and fields.Date.from_string(
                    att.date_to) < day_date)):
            if start_time and self.float_to_time(
                    attendance.hour_to) < start_time:
                continue
            if end_time and self.float_to_time(attendance.hour_from) > end_time:
                continue
            attendances |= attendance
        return attendances

    def _iter_day_attendance_intervals(self, day_date, start_time, end_time):
        """ Get an iterator of all interval of current day attendances. """
        for calendar_working_day in self._get_day_attendances(day_date,
                                                              start_time,
                                                              end_time):
            from_time = self.float_to_time(calendar_working_day.hour_from)
            to_time = self.float_to_time(calendar_working_day.hour_to)
            dt_f = datetime.datetime.combine(day_date,
                                             max(from_time, start_time))
            dt_t = datetime.datetime.combine(day_date, min(to_time, end_time))
            yield self._interval_new(dt_f, dt_t,
                                     {'attendances': calendar_working_day})
