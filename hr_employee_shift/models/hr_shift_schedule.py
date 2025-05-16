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
from odoo import api, fields, models, _


class HrShiftSchedule(models.Model):
    """Represents the shift schedule for employees within the HR module."""
    _name = 'hr.shift.schedule'
    _description = "Represents the shift schedule"

    start_date = fields.Date(string="Date From", required=True,
                             help="Starting date for the shift")
    end_date = fields.Date(string="Date To", required=True,
                           help="Ending date for the shift")
    rel_hr_schedule = fields.Many2one('hr.contract',string="Contract", help="Connection to employee contract")
    hr_shift = fields.Many2one('resource.calendar', string="Shift",
                               required=True, help="Scheduled Shift")
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Current Company")

    @api.onchange('start_date', 'end_date')
    def get_department(self):
        """Adding domain to  the hr_shift field"""
        hr_department = None
        if self.start_date:
            hr_department = self.rel_hr_schedule.department_id.id
        return {
            'domain': {
                'hr_shift': [('hr_department', '=', hr_department)]
            }
        }

    def write(self, vals):
        """Overrides the default write method to ensure there are no overlapping
        shift schedules before updating a record.
        This method first checks for any overlapping shift schedules, If no
        overlaps are found, it proceeds to update the record using the parent class's `write` method."""
        self._check_overlap(vals)
        return super(HrShiftSchedule, self).write(vals)

    @api.model_create_multi
    def create(self, vals):
        """The create method in the HrShift Schedule class overrides the parent
         class's create function to check for overlapping shift schedules before
          creating a new record."""
        self._check_overlap(vals)
        return super(HrShiftSchedule, self).create(vals)

    def _check_overlap(self, vals):
        """The _check_ove rlap method checks for overlapping shift schedules and
         validates that the start date is before the end date. If an overlap is
         detected or the start date is after the end date, it raises a warning."""
        print(vals)
        for val in vals:
            if val.get('start_date', False) and val.get('end_date', False):
                shifts = self.env['hr.shift.schedule'].search(
                    [('rel_hr_schedule', '=', val.get('rel_hr_schedule'))])
                for each in shifts:
                    if each != shifts[-1]:
                        if each.end_date >= val.get(
                                'start_date') or each.start_date >= val.get(
                            'start_date'):
                            raise Warning(
                                _('The dates may not overlap with one another.'))
                if val.get('start_date') > val.get('end_date'):
                    raise Warning(_('Start date should be less than end date.'))
            return True
