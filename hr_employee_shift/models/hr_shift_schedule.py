# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from datetime import timedelta
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class HrShiftSchedule(models.Model):
    """Represents the shift schedule for employees within the HR module."""
    _name = 'hr.shift.schedule'
    _description = "Represents the shift schedule"
    _order = 'start_date desc, id desc'

    start_date = fields.Date(string="Date From", required=True,
                             help="Starting date for the shift")
    end_date = fields.Date(string="Date To", required=True,
                           help="Ending date for the shift")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Connection to employee record")
    hr_shift = fields.Many2one('resource.calendar', string="Shift",
                               required=True, help="Scheduled Shift")
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Current Company")

    @api.onchange('start_date', 'end_date')
    def get_department(self):
        """Adding domain to the hr_shift field"""
        hr_department = None
        if self.start_date and self.employee_id:
            hr_department = self.employee_id.department_id.id
        return {
            'domain': {
                'hr_shift': [('hr_department', '=', hr_department)] if hr_department else []
            }
        }

    def write(self, vals):
        """Overrides the default write method to ensure there are no overlapping
        shift schedules before updating a record."""
        self._check_overlap([vals], is_write=True)
        return super(HrShiftSchedule, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """The create method overrides the parent
         class's create function to check for overlapping shift schedules before
          creating a new record."""
        self._check_overlap(vals_list)
        return super(HrShiftSchedule, self).create(vals_list)

    def _check_overlap(self, vals_list, is_write=False):
        """Checks for overlapping shift schedules and
         validates that the start date is before the end date."""
        from odoo.exceptions import ValidationError
        for val in vals_list:
            start = val.get('start_date') or (self.start_date if is_write else False)
            end = val.get('end_date') or (self.end_date if is_write else False)
            emp_id = val.get('employee_id') or (self.employee_id.id if is_write else False)

            if start and end and emp_id:
                if start > end:
                    raise ValidationError(_('Start date should be less than or equal to end date.'))
                
                domain = [
                    ('employee_id', '=', emp_id),
                    ('id', '!=', self.id if is_write else False),
                    '|', '|',
                    '&', ('start_date', '<=', start), ('end_date', '>=', start),
                    '&', ('start_date', '<=', end), ('end_date', '>=', end),
                    '&', ('start_date', '>=', start), ('end_date', '<=', end)
                ]
                overlaps = self.env['hr.shift.schedule'].search(domain)
                if overlaps:
                    emp_name = self.env['hr.employee'].browse(emp_id).name
                    raise ValidationError(_('The dates may not overlap with another shift for the employee: %s.') % emp_name)
        return True

    @api.model
    def _cron_send_shift_reminders(self):
        """Send a reminder if a shift schedule starts tomorrow."""
        today = fields.Date.context_today(self)
        tomorrow = today + timedelta(days=1)
        _logger.info("Shift Reminder Cron: Checking for shifts starting on %s", tomorrow)
        # Find all shift schedules that START tomorrow
        shifts_starting_tomorrow = self.search([('start_date', '=', tomorrow)])
        notified_count = 0
        for shift in shifts_starting_tomorrow:
            employee = shift.employee_id
            calendar = shift.hr_shift
            if calendar and employee:
                msg = _("Reminder: You are scheduled to start the %s tomorrow (%s).") % (calendar.name, tomorrow.strftime('%Y-%m-%d'))
                partner_ids = employee.user_id.partner_id.ids if employee.user_id else []
                _logger.info("Shift Reminder Cron: Notifying employee %s (Partner %s). Shift %s starts tomorrow.", 
                             employee.name, partner_ids, calendar.name)
                if hasattr(employee, 'message_post'):
                    employee.message_post(body=msg, partner_ids=partner_ids, message_type='comment')
                notified_count += 1
        _logger.info("Shift Reminder Cron: Finished. Notified %d employees.", notified_count)
