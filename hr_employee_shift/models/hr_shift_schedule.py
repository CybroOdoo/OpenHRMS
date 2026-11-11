# -*- coding: utf-8 -*-
#############################################################################
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
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
                                 related='employee_id.company_id', store=True, readonly=False,
                                 help="Current Company")

    @api.onchange('employee_id', 'start_date', 'end_date')
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

    @api.constrains('employee_id', 'start_date', 'end_date')
    def _check_overlap(self):
        """Checks for overlapping shift schedules and
        validates that the start date is before the end date."""
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError(_('Start date should be less than or equal to end date.'))

                if record.employee_id:
                    domain = [
                        ('employee_id', '=', record.employee_id.id),
                        ('id', '!=', record.id),
                        ('start_date', '<=', record.end_date),
                        ('end_date', '>=', record.start_date),
                    ]
                    if self.search_count(domain):
                        raise ValidationError(
                            _('The dates may not overlap with another shift for the employee: %s.') % record.employee_id.name
                        )

    @api.model
    def _cron_send_shift_reminders(self):
        """Send a reminder if a shift schedule starts tomorrow."""
        import logging
        _logger = logging.getLogger(__name__)
        from datetime import timedelta
        
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
