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
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    """Inherited model for managing HR Leave requests."""
    _inherit = 'hr.leave'

    remaining_leaves = fields.Float(
        string='Remaining Legal Leaves',
        compute='_compute_remaining_leaves',
        help="Remaining legal leaves"
    )
    overlapping_leaves_ids = fields.Many2many('hr.leave',
                                              compute='_compute_overlapping_leaves_ids',
                                              string='Overlapping Leaves',
                                              help="Overlapping leaves of"
                                                   " employees.")
    pending_task_ids = fields.One2many('pending.task',
                                       'leave_id',
                                       string='Pending Tasks',
                                       help="Details of pending tasks")
    holiday_managers_ids = fields.Many2many('res.users',
                                            compute='_compute_holiday_managers_ids',
                                            help="Responsible holiday managers")
    flight_ticket_ids = fields.One2many('hr.flight.ticket',
                                        'leave_id',
                                        string='Flight Ticket',
                                        help="Flight ticket Details")
    expense_account_id = fields.Many2one('account.account',
                                         string='Expense Account',
                                         help='Expense account to account the '
                                              'flight expenses.')
    leave_salary = fields.Selection([('0', 'Basic'), ('1', 'Gross')],
                                    string='Leave Salary',
                                    help='Details about leave salary of'
                                         ' employee.')

    @api.depends('date_from', 'date_to', 'department_id')
    def _compute_overlapping_leaves_ids(self):
        """Compute function over overlapping leaves"""
        for rec in self:
            if rec.date_from and rec.date_to and rec.department_id:
                leaves = rec.env['hr.leave'].search([
                    ('state', '=', 'validate'),
                    ('department_id', '=', rec.department_id.id),
                    ('id', '!=', rec.id or 0),
                    ('date_from', '<=', rec.date_to),
                    ('date_to', '>=', rec.date_from),
                ])
                rec.overlapping_leaves_ids = leaves
            else:
                rec.overlapping_leaves_ids = False

    def action_approve(self, check_state=True):
        """This method is used to approve leave requests. If there are pending tasks,
        opens task reassignment; otherwise delegates to super().action_approve."""
        has_tasks = any(holiday.pending_task_ids for holiday in self)
        if has_tasks:
            if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
                raise UserError(
                    _('Only an HR Officer or Manager can approve leave requests.'))
            for holiday in self:
                if holiday.state != 'confirm':
                    raise UserError(
                        _('Leave request must be confirmed ("To Approve") in '
                          'order to approve it.'))
                if holiday.pending_task_ids and holiday.user_id:
                    ctx = dict(self.env.context or {})
                    ctx.update({
                        'default_leave_req_id': self.id,
                    })
                    return {
                        'name': _('Re-Assign Task'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'task.reassign',
                        'target': 'new',
                        'context': ctx,
                    }
        return super().action_approve(check_state=check_state)

    def action_book_ticket(self):
        """Open the form view to book a flight ticket for the current
         leave request."""
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(
                _('Only an HR Officer or Manager can book flight tickets.'))
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_leave_id': self.id,
        })
        return {
            'name': _('Book Flight Ticket'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'hr_vacation_mngmt.view_hr_book_flight_ticket_form').id,
            'res_model': 'hr.flight.ticket',
            'target': 'new',
            'context': ctx,
        }

    def _compute_holiday_managers_ids(self):
        """Retrieve the IDs of users belonging to the
         'Holiday Managers' group."""
        group = self.env.ref('hr_holidays.group_hr_holidays_manager', raise_if_not_found=False)
        users = (group.all_user_ids or group.user_ids) if group else self.env['res.users']
        for rec in self:
            rec.holiday_managers_ids = users

    def action_view_flight_ticket(self):
        """Open the form view for the first flight ticket associated
         with this employee."""
        self.ensure_one()
        return {
            'name': _('Flight Ticket'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.flight.ticket',
            'target': 'current',
            'res_id': self.flight_ticket_ids[0].id if self.flight_ticket_ids else False,
        }

    @api.model
    def send_leave_reminder(self):
        """Send leave reminders to holiday managers for validated leave
         requests."""
        leave_request = self.env['hr.leave'].search(
            [('state', '=', 'validate')])
        leave_reminder = (
            self.env['ir.config_parameter'].sudo().get_bool('hr_vacation_mngmt.leave_reminder')
            or self.env['ir.config_parameter'].sudo().get_bool('leave_reminder')
        )
        reminder_day_before = (
            self.env['ir.config_parameter'].sudo().get_int('hr_vacation_mngmt.reminder_day_before', default=0)
            or self.env['ir.config_parameter'].sudo().get_int('reminder_day_before', default=0)
        )
        mail_template = self.env.ref(
            'hr_vacation_mngmt.email_template_hr_leave_reminder_mail',
            raise_if_not_found=False
        )
        holiday_managers = self.env.ref(
            'hr_holidays.group_hr_holidays_manager',
            raise_if_not_found=False
        )
        managers = (holiday_managers.all_user_ids or holiday_managers.user_ids) if holiday_managers else self.env['res.users']
        if leave_reminder and mail_template:
            for request in leave_request:
                if request.date_from:
                    from_date = request.date_from
                    if reminder_day_before == 0:
                        prev_reminder_day = request.date_from
                    else:
                        prev_reminder_day = from_date - timedelta(
                            days=reminder_day_before)
                    if prev_reminder_day.date() == fields.Date.today():
                        for manager in managers:
                            if manager.email:
                                mail_template.sudo().send_mail(
                                    request.id,
                                    force_send=True,
                                    email_values={'email_to': manager.email},
                                )

    @api.depends('employee_id', 'work_entry_type_id', 'virtual_remaining_leaves')
    def _compute_remaining_leaves(self):
        """Compute the remaining legal leaves based on the employee's
        available time off for the selected time type."""
        for leave in self:
            if not leave.employee_id or not leave.work_entry_type_id:
                leave.remaining_leaves = 0.0
            else:
                leave.remaining_leaves = leave.virtual_remaining_leaves or 0.0