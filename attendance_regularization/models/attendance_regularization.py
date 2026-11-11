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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AttendanceRegular(models.Model):
    """Model to record regularization attendance"""
    _name = 'attendance.regular'
    _rec_name = 'employee_id'
    _rec_names_search = ('employee_id',)
    _description = 'Attendance Regularization'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee_id(self):
        """Get the ID of the currently logged-in employee"""
        return self.env.user.employee_id.id or self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid),
        ], limit=1).id

    reg_category = fields.Many2one(
        'reg.categories',
        string='Regularization Category',
        required=True,
        help='Choose the category of attendance regularization',
    )
    from_date = fields.Datetime(
        required=True,
        help='Start Date',
    )
    to_date = fields.Datetime(
        required=True,
        help='End Date',
    )
    reg_reason = fields.Text(
        string='Reason',
        required=True,
        help='Reason for the attendance regularization',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        default=lambda self: self._default_employee_id(),
        required=True,
        help='Employee',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('reject', 'Rejected'),
            ('approved', 'Approved'),
        ],
        default='draft',
        copy=False,
        tracking=True,
        help='Status of record',
    )

    @api.constrains('employee_id')
    def _check_employee_id(self):
        """Validate that non-manager users can only submit regularization requests for themselves."""
        is_manager = self.env.is_superuser() or self.env.user.has_group('hr_attendance.group_hr_attendance_manager')
        for rec in self:
            if not is_manager:
                user_employee = self.env.user.employee_id or self.env['hr.employee'].search([
                    ('user_id', '=', self.env.uid),
                ], limit=1)
                if not user_employee or rec.employee_id != user_employee:
                    raise ValidationError(self.env._("You can only submit attendance regularization requests for yourself."))

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        """Ensure that To Date is greater than or equal to From Date."""
        for rec in self:
            if rec.from_date and rec.to_date and rec.from_date > rec.to_date:
                raise ValidationError(self.env._('"To Date" must be greater than or equal to "From Date".'))

    def action_submit(self):
        """Change state to 'requested' upon submission"""
        for rec in self:
            rec.state = 'requested'

    def action_approve(self):
        """Approve the attendance regularization and create hr.attendance record"""
        for rec in self:
            rec.state = 'approved'
            self.env['hr.attendance'].sudo().create({
                'check_in': rec.from_date,
                'check_out': rec.to_date,
                'employee_id': rec.employee_id.id,
                'regularization': True,
            })

    def action_reject(self):
        """Reject the attendance regularization"""
        for rec in self:
            rec.state = 'reject'
