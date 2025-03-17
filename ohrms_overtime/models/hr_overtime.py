# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
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
from dateutil import relativedelta
import pandas as pd
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

    name = fields.Char('Name', readonly=True,
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
                                      default=lambda self: self.env.uid,
                                      store=True,
                                      help="User currently logged in.")
    is_current_user = fields.Boolean('Current User ',
                                     help="Boolean field indicating "
                                          "weather the current user is "
                                          "associated with the overtime "
                                          "request.")
    project_id = fields.Many2one('project.project',
                                 string="Project", help="Project associated "
                                                        "with the overtime "
                                                        "request.")
    project_manager_id = fields.Many2one('res.users',
                                         string="Project Manager",
                                         help="Manager of the project "
                                              "associated with the overtime "
                                              "request.")
    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  help="Contract of the employee")
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
    cash_hrs_amount = fields.Float(string='Overtime Amount', readonly=True,
                                   help="Amount for overtime based on hours")
    cash_day_amount = fields.Float(string='Overtime Amount', readonly=True,
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
            if sheet.project_id:
                sheet.update({
                    'project_manager_id': sheet.project_id.user_id.id,
                })

    @api.depends('date_from', 'date_to')
    def _get_days(self):
        """  Calculate the number of days or hours based on the duration type"""
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError(
                        'Start Date must be less than End Date')
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                start_dt = fields.Datetime.from_string(sheet.date_from)
                finish_dt = fields.Datetime.from_string(sheet.date_to)
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours
                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))
                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                sheet.update({
                    'days_no_tmp': hours if sheet.duration_type == 'hours' else days_no,
                })

    @api.onchange('overtime_type_id')
    def _get_hour_amount(self):
        """Calculate the overtime amount based on the selected overtime type,
        duration type, and contract details."""
        if self.overtime_type_id.rule_line_ids and self.duration_type == 'hours':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_hour:
                        cash_amount = self.contract_id.over_hour * recd.hrs_amount
                        self.cash_hrs_amount = cash_amount
                    else:
                        raise UserError(
                            _("Hour Overtime Needs Hour Wage in Employee Contract."))
        elif self.overtime_type_id.rule_line_ids and self.duration_type == 'days':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_day:
                        cash_amount = self.contract_id.over_day * recd.hrs_amount
                        self.cash_day_amount = cash_amount
                    else:
                        raise UserError(
                            _("Day Overtime Needs Day Wage in Employee Contract."))

    def action_submit_to_finance(self):
        """Submit the overtime request for finance approval."""
        return self.sudo().write({
            'state': 'f_approve'
        })

    def action_approve(self):
        """Approve the overtime request and create a leave record if the type
        is 'leave'"""
        if self.overtime_type_id.type == 'leave':
            if self.duration_type == 'days':
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type_id.id,
                    'number_of_days': self.days_no_tmp,
                    'notes': self.desc,
                    'employee_id': self.employee_id.id,
                    'state': 'confirm',
                    'date_from': self.date_from.date(),
                    'date_to': self.date_to.date()
                }
            else:
                day_hour = self.days_no_tmp / HOURS_PER_DAY
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type_id.id,
                    'number_of_days': day_hour,
                    'notes': self.desc,
                    'employee_id': self.employee_id.id,
                    'state': 'confirm',
                    'date_from': self.date_from.date(),
                    'date_to': self.date_to.date()
                }
            holiday = self.env['hr.leave.allocation'].sudo().create(
                holiday_vals)
            self.leave_id = holiday.id
        return self.sudo().write({
            'state': 'approved',
        })

    def action_reject(self):
        """Set the state of the overtime request to 'refused'."""
        self.state = 'refused'

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

    @api.model
    def create(self, values):
        """ Create a new overtime request with a unique sequence number"""
        seq = self.env['ir.sequence'].next_by_code('hr.overtime') or '/'
        values['name'] = seq
        return super(HrOvertime, self.sudo()).create(values)

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
        """ Update the 'public_holiday' field based on the presence of public
        holidays in the selected date range.Update the 'attendance_ids' field
        based on the attendance records within the selected date range."""
        holiday = False
        if self.contract_id and self.date_from and self.date_to:
            for leaves in self.contract_id.resource_calendar_id.global_leave_ids:
                leave_dates = pd.date_range(leaves.date_from,
                                            leaves.date_to).date
                overtime_dates = pd.date_range(self.date_from,
                                               self.date_to).date
                for over_time in overtime_dates:
                    for leave_date in leave_dates:
                        if leave_date == over_time:
                            holiday = True
            if holiday:
                self.write({
                    'public_holiday': 'You have Public Holidays in your Overtime request.'})
            else:
                self.write({'public_holiday': ' '})
            hr_attendance = self.env['hr.attendance'].search(
                [('check_in', '>=', self.date_from),
                 ('check_in', '<=', self.date_to),
                 ('employee_id', '=', self.employee_id.id)])
            self.update({
                'attendance_ids': [(6, 0, hr_attendance.ids)]
            })
