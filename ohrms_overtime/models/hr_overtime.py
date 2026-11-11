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
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.utils import HOURS_PER_DAY


class HrOvertime(models.Model):
    """ Model to manage Overtime requests for employees."""
    _name = 'hr.overtime'
    _description = "HR Overtime"
    _inherit = ['mail.thread']

    def _get_employee_domain(self):
        """Get the domain for the employee field based on the current user."""
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    def _default_employee(self):
        """ Get the default employee based on the current user."""
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)],
                                              limit=1)

    @api.onchange('days_no_tmp')
    def _onchange_days_no_tmp(self):
        """Update the 'days_no' field when 'days_no_tmp' changes."""
        self.days_no = self.days_no_tmp

    name = fields.Char('Reference', readonly=True, copy=False,
                       default=lambda self: _('New'),
                       help="Name of the overtime request.")
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain=_get_employee_domain,
                                  default=lambda
                                      self: self.env.user.employee_id.id,
                                  required=True,
                                  help="Employee for whom the overtime request "
                                       "is made")
    department_id = fields.Many2one('hr.department',
                                    string="Department",
                                    related="employee_id.department_id",
                                    help="Department of the employee.")
    job_id = fields.Many2one('hr.job', string="Job",
                             related="employee_id.job_id",
                             help="Job position of the employee.")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id",
                                 store=True, help="Manager of the employee.")
    current_user_id = fields.Many2one('res.users',
                                      string="Current User",
                                      related='employee_id.user_id',
                                      store=True,
                                      help="User currently logged in.")
    is_current_user = fields.Boolean(
        'Current User',
        compute='_compute_is_current_user',
        help="Boolean field indicating whether the current user is "
             "associated with the overtime request.")

    @api.depends('employee_id')
    def _compute_is_current_user(self):
        """Compute whether the current user is associated with the overtime request."""
        for rec in self:
            rec.is_current_user = bool(
                rec.employee_id.user_id and rec.employee_id.user_id == self.env.user
            )
    project_id = fields.Many2one('project.project',
                                 string="Project", help="Project associated "
                                                        "with the overtime "
                                                        "request.")
    project_manager_id = fields.Many2one('res.users',
                                         string="Project Manager",
                                         compute='_get_project_manager',
                                         store=True, readonly=False,
                                         help="Manager of the project "
                                              "associated with the overtime "
                                              "request.")
    contract_id = fields.Many2one('hr.version', string="Contract",
                                  compute='_compute_contract_id',
                                  store=True, readonly=False, precompute=True,
                                  help="Contract of the employee")

    @api.depends('employee_id')
    def _compute_contract_id(self):
        for rec in self:
            if rec.employee_id:
                rec.contract_id = rec.employee_id.current_version_id or self.env['hr.version'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('active', '=', True),
                ], limit=1)
            else:
                rec.contract_id = False
    date_from = fields.Datetime('Date From', help="Start date and time of"
                                                  " the overtime request.")
    date_to = fields.Datetime('Date to', help="End date and time of the "
                                              "overtime request.")
    days_no_tmp = fields.Float('Hours', compute="_get_days", store=True,
                               help="Temporary field to store the calculated "
                                    "hours for the overtime request.")
    days_no = fields.Float('No. of Days', store=True,
                           help="Number of days for the overtime request.")
    desc = fields.Text('Description', help="Description of the overtime "
                                           "request.")
    state = fields.Selection([('draft', 'Draft'),
                              ('f_approve', 'Waiting'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], string="state",
                             default="draft", help="State of the overtime "
                                                   "request.")
    cancel_reason = fields.Text('Refuse Reason',
                                help="Reason for refusing "
                                     "the overtime request.")
    leave_id = fields.Many2one('hr.leave.allocation',
                               string="Leave ID", help="Leave associated with "
                                                       "the overtime request.")
    attchd_copy = fields.Binary('Attach A File',
                                help="Attachment file for the overtime request")
    attchd_copy_name = fields.Char('File Name',
                                   help="Name of the attached file")
    type = fields.Selection([('cash', 'Cash'), ('leave', 'Leave')],
                            default="leave", required=True, string="Type",
                            help="Type of the overtime request")
    overtime_type_id = fields.Many2one('overtime.type',
                                       domain="[('type','=',type), "
                                              "('duration_type','=',"
                                              "duration_type)]",
                                       help="Overtime Type")
    public_holiday = fields.Char(string='Public Holiday', readonly=True,
                                 help="Indicates if there are public holidays "
                                      "in the overtime request period")
    attendance_ids = fields.Many2many('hr.attendance',
                                      string='Attendance',
                                      help="Attendance records associated with "
                                           "the overtime request.")
    work_schedule_ids = fields.One2many(
        related='employee_id.resource_calendar_id.attendance_ids',
        help="Work schedule of the employee")
    global_leaves_ids = fields.One2many(
        related='employee_id.resource_calendar_id.global_leave_ids',
        help="Global leaves of the employee")
    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')],
                                     string="Duration Type", default="hours",
                                     required=True,
                                     help="Type of duration for the overtime "
                                          "request")
    cash_hrs_amount = fields.Float(string='Overtime Amount',
                                   compute='_compute_cash_amount',
                                   store=True, readonly=False,
                                   help="Amount for overtime based on hours")
    cash_day_amount = fields.Float(string='Overtime Amount',
                                   compute='_compute_cash_amount',
                                   store=True, readonly=False,
                                   help="Amount for overtime based on days")
    is_payslip_paid = fields.Boolean('Paid in Payslip', readonly=True,
                                     help="Indicates whether the overtime is paid "
                                          "in the payslip.")

    @api.onchange('employee_id')
    def _get_defaults(self):
        """ Set default values for fields based on the selected employee."""
        for sheet in self:
            if sheet.employee_id:
                sheet.update({
                    'department_id': sheet.employee_id.department_id.id,
                    'job_id': sheet.employee_id.job_id.id,
                    'manager_id': sheet.sudo().employee_id.parent_id.user_id.id,
                })

    @api.depends('project_id')
    def _get_project_manager(self):
        """Update the 'project_manager_id' based on the selected project."""
        for sheet in self:
            sheet.project_manager_id = sheet.project_id.user_id.id if sheet.project_id else False

    @api.depends('date_from', 'date_to', 'duration_type')
    def _get_days(self):
        """Calculate the number of days or hours based on the duration type."""
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                if sheet.date_from > sheet.date_to:
                    raise ValidationError(
                        _('Start Date must be less than End Date'))
                diff = sheet.date_to - sheet.date_from
                total_hours = round(diff.total_seconds() / 3600.0, 2)
                days_no = round(diff.total_seconds() / (24.0 * 3600.0), 2)
                sheet.days_no_tmp = total_hours if sheet.duration_type == 'hours' else days_no
                sheet.days_no = sheet.days_no_tmp
            else:
                sheet.days_no_tmp = 0.0
                sheet.days_no = 0.0

    @api.depends('type', 'overtime_type_id', 'overtime_type_id.rule_line_ids', 'duration_type',
                 'days_no_tmp', 'contract_id', 'contract_id.over_hour', 'contract_id.over_day')
    def _compute_cash_amount(self):
        """Calculate the overtime amount based on the selected overtime type,
        duration type, and contract details."""
        for rec in self:
            hrs_amount = 0.0
            day_amount = 0.0
            if rec.type == 'cash' and rec.overtime_type_id and rec.contract_id:
                if rec.duration_type == 'hours':
                    rate = 1.0
                    if rec.overtime_type_id.rule_line_ids:
                        for rule in rec.overtime_type_id.rule_line_ids:
                            if rule.from_hrs < rec.days_no_tmp <= rule.to_hrs:
                                rate = rule.hrs_amount
                                break
                    hrs_amount = round((rec.contract_id.over_hour or 0.0) * rate * rec.days_no_tmp, 2)
                elif rec.duration_type == 'days':
                    rate = 1.0
                    if rec.overtime_type_id.rule_line_ids:
                        for rule in rec.overtime_type_id.rule_line_ids:
                            if rule.from_hrs < rec.days_no_tmp <= rule.to_hrs:
                                rate = rule.hrs_amount
                                break
                    day_amount = round((rec.contract_id.over_day or 0.0) * rate * rec.days_no_tmp, 2)
            rec.cash_hrs_amount = hrs_amount
            rec.cash_day_amount = day_amount

    def _get_hour_amount(self):
        """Alias for backward compatibility."""
        self._compute_cash_amount()

    def action_submit_to_finance(self):
        """Submit the overtime request for finance approval."""
        return self.sudo().write({
            'state': 'f_approve'
        })

    def action_approve(self):
        """Approve the overtime request and create a leave record if the type
        is 'leave'"""
        for rec in self:
            if not rec.overtime_type_id:
                raise UserError(_("Please select an Overtime Type before approving."))

            vals = {'state': 'approved'}
            if rec.overtime_type_id.type == 'leave':
                if not rec.overtime_type_id.leave_type_id:
                    raise UserError(
                        _("Please configure a Leave Type on Overtime Type '%s'.") % rec.overtime_type_id.name)
                date_from = rec.date_from.date() if rec.date_from else fields.Date.context_today(rec)
                date_to = rec.date_to.date() if rec.date_to else fields.Date.context_today(rec)
                if rec.duration_type == 'days':
                    holiday_vals = {
                        'name': 'Overtime',
                        'work_entry_type_id': rec.overtime_type_id.leave_type_id.id,
                        'number_of_days': rec.days_no_tmp,
                        'notes': rec.desc,
                        'employee_id': rec.employee_id.id,
                        'state': 'confirm',
                        'date_from': date_from,
                        'date_to': date_to,
                    }
                else:
                    day_hour = rec.days_no_tmp / HOURS_PER_DAY
                    holiday_vals = {
                        'name': 'Overtime',
                        'work_entry_type_id': rec.overtime_type_id.leave_type_id.id,
                        'number_of_days': day_hour,
                        'notes': rec.desc,
                        'employee_id': rec.employee_id.id,
                        'state': 'confirm',
                        'date_from': date_from,
                        'date_to': date_to,
                    }
                holiday = self.env['hr.leave.allocation'].sudo().create(holiday_vals)
                vals['leave_id'] = holiday.id
            elif rec.overtime_type_id.type == 'cash':
                if not rec.contract_id:
                    raise UserError(_("Please link an active contract to the employee before approving cash overtime."))
                if rec.duration_type == 'hours' and not rec.contract_id.over_hour:
                    raise UserError(_("Hour Overtime Needs Hour Wage in Employee Contract."))
                if rec.duration_type == 'days' and not rec.contract_id.over_day:
                    raise UserError(_("Day Overtime Needs Day Wage in Employee Contract."))
                rec._compute_cash_amount()
                vals['cash_hrs_amount'] = rec.cash_hrs_amount
                vals['cash_day_amount'] = rec.cash_day_amount
            rec.sudo().write(vals)
        return True

    def action_reject(self):
        """Set the state of the overtime request to 'refused'."""
        self.write({'state': 'refused'})

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """Check if there are overlapping overtime requests for the same
        employee on the same day."""
        for req in self:
            domain = [
                ('date_from', '<=', req.date_to),
                ('date_to', '>=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            no_of_holidays = self.search_count(domain)
            if no_of_holidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that overlaps on '
                    'same day!'))

    @api.model_create_multi
    def create(self, vals_list):
        """Create a new overtime request with a unique sequence number."""
        for vals in vals_list:
            if vals.get('name', _('New')) in (_('New'), '/'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.overtime') or _('New')
        return super(HrOvertime, self.sudo()).create(vals_list)

    def unlink(self):
        """Unlink the overtime request, preventing deletion if it's not in
        'draft' state."""
        for overtime in self.filtered(
                lambda overtime: overtime.state != 'draft'):
            raise UserError(
                _('You cannot delete TIL request which is not in draft state.'))
        return super(HrOvertime, self).unlink()

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_date(self):
        """Update the 'public_holiday' field based on the presence of public
        holidays in the selected date range. Update the 'attendance_ids' field
        based on the attendance records within the selected date range."""
        for rec in self:
            holiday = False
            calendar = (rec.contract_id.resource_calendar_id
                        if rec.contract_id and hasattr(rec.contract_id, 'resource_calendar_id') and rec.contract_id.resource_calendar_id
                        else rec.employee_id.resource_calendar_id)
            if calendar and rec.date_from and rec.date_to:
                for leaves in calendar.global_leave_ids:
                    if leaves.date_from and leaves.date_to:
                        if leaves.date_from <= rec.date_to and leaves.date_to >= rec.date_from:
                            holiday = True
                            break
            if holiday:
                rec.public_holiday = _('You have Public Holidays in your Overtime request.')
            else:
                rec.public_holiday = False

            if rec.date_from and rec.date_to and rec.employee_id:
                hr_attendance = self.env['hr.attendance'].search([
                    ('check_in', '>=', rec.date_from),
                    ('check_in', '<=', rec.date_to),
                    ('employee_id', '=', rec.employee_id.id),
                ])
                rec.attendance_ids = hr_attendance
            else:
                rec.attendance_ids = False
