# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo.exceptions import ValidationError

date_format = "%Y-%m-%d"
RESIGNATION_TYPE = [('resigned', 'Normal Resignation'),
                    ('fired', 'Fired by the company')]


class HrResignation(models.Model):
    """
     Model for HR Resignations.
     This model is used to track employee resignations.
    """
    _name = 'hr.resignation'
    _description = 'HR Resignation'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'

    name = fields.Char(string='Order Reference', copy=False,
                       readonly=True, index=True,
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  default=lambda
                                      self: self.env.user.employee_id.id,
                                  help='Name of the employee for '
                                       'whom the request is creating')
    department_id = fields.Many2one('hr.department', string="Department",
                                    related='employee_id.department_id',
                                    help='Department of the employee')
    resign_confirm_date = fields.Date(string="Confirmed Date",
                                      help='Date on which the request '
                                           'is confirmed by the employee.',
                                      track_visibility="always")
    approved_revealing_date = fields.Date(
        string="Approved Last Day Of Employee",
        help='Date on which the request is confirmed by the manager.',
        track_visibility="always")
    joined_date = fields.Date(string="Join Date",
                              help='Joining date of the employee.'
                                   'i.e Start date of the first contract')
    expected_revealing_date = fields.Date(string="Last Day of Employee",
                                          required=True,
                                          help='Employee requested date on '
                                               'which employee is revealing '
                                               'from the company.')
    reason = fields.Text(string="Reason", required=True,
                         help='Specify reason for leaving the company')
    notice_period = fields.Char(string="Notice Period",
                                help="Notice Period of the employee.")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('approved', 'Approved'),
         ('cancel', 'Rejected')],
        string='Status', default='draft', track_visibility="always")
    resignation_type = fields.Selection(selection=RESIGNATION_TYPE,
                                        help="Select the type of resignation: "
                                             "normal resignation or "
                                             "fired by the company")
    change_employee = fields.Boolean(string="Change Employee",
                                     compute="_compute_change_employee",
                                     help="Checks , if the user has permission"
                                          " to change the employee")
    employee_contract = fields.Char(String="Contract")

    @api.depends('employee_id')
    def _compute_change_employee(self):
        """ Check whether the user
        has the permission to change the employee"""
        res_user = self.env['res.users'].browse(self._uid)
        self.change_employee = res_user.has_group('hr.group_hr_user')

    @api.constrains('employee_id')
    def _check_employee_id(self):
        """" Constraint method to check if the current user has the permission
        to create
         a resignation request for the specified employee.
        """
        for resignation in self:
            if not self.env.user.has_group('hr.group_hr_user'):
                if (resignation.employee_id.user_id.id and
                        resignation.employee_id.user_id.id != self.env.uid):
                    raise ValidationError(
                        _('You cannot create a request for other employees'))

    @api.constrains('joined_date')
    def _check_joined_date(self):
        """
        Check if there is an active resignation request for the
        same employee with a confirmed or approved state, based on the
        'joined_date'
        of the current resignation.
        """
        for resignation in self:
            resignation_request = self.env['hr.resignation'].search(
                [('employee_id', '=', resignation.employee_id.id),
                 ('state', 'in', ['confirm', 'approved'])])
            if resignation_request:
                raise ValidationError(
                    _('There is a resignation request in confirmed or'
                      ' approved state for this employee'))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """
        Method triggered when the 'employee_id' field is changed.
        """
        self.joined_date = self.employee_id.joining_date
        if self.employee_id:
            resignation_request = self.env['hr.resignation'].search(
                [('employee_id', '=', self.employee_id.id),
                 ('state', 'in', ['confirm', 'approved'])])
            if resignation_request:
                raise ValidationError(
                    _('There is a resignation request in confirmed or'
                      ' approved state for this employee'))
            employee_contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id)])
            for contracts in employee_contract:
                if contracts.state == 'open':
                    self.employee_contract = contracts.name
                    self.notice_period = contracts.notice_days

    @api.model
    def create(self, vals):
        """
            Override of the create method to assign a sequence for the record.
        """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.resignation') or _('New')
        return super(HrResignation, self).create(vals)

    def action_confirm_resignation(self):
        """
        Method triggered by the 'Confirm' button to confirm the
        resignation request.
        """
        for resignation in self:
            if resignation.joined_date:
                if (resignation.joined_date >=
                        resignation.expected_revealing_date):
                    raise ValidationError(
                        _('Last date of the Employee must '
                          'be anterior to Joining date'))
            else:
                raise ValidationError(
                    _('Please set a Joining Date for employee'))
            resignation.state = 'confirm'
            resignation.resign_confirm_date = str(fields.Datetime.now())

    def action_cancel_resignation(self):
        """
        Method triggered by the 'Cancel' button to cancel the
        resignation request.
        """
        for resignation in self:
            resignation.state = 'cancel'

    def action_reject_resignation(self):
        """
            Method triggered by the 'Reject' button to reject the
            resignation request.
        """
        for resignation in self:
            resignation.state = 'cancel'

    def action_reset_to_draft(self):
        """
        Method triggered by the 'Set to Draft' button to reset the
        resignation request to the 'draft' state.
        """
        for resignation in self:
            resignation.state = 'draft'
            resignation.employee_id.active = True
            resignation.employee_id.resigned = False
            resignation.employee_id.fired = False

    def action_approve_resignation(self):
        """
               Method triggered by the 'Approve' button to
               approve the resignation.
        """
        for resignation in self:
            if (resignation.expected_revealing_date and
                    resignation.resign_confirm_date):
                employee_contract = self.env['hr.contract'].search(
                    [('employee_id', '=', self.employee_id.id)])
                if not employee_contract:
                    raise ValidationError(
                        _("There are no Contracts found for this employee"))
                for contract in employee_contract:
                    if contract.state == 'open':
                        resignation.employee_contract = contract.name
                        resignation.state = 'approved'
                        resignation.approved_revealing_date = (
                                resignation.resign_confirm_date + timedelta(
                            days=contract.notice_days))
                    else:
                        resignation.approved_revealing_date = (
                            resignation.expected_revealing_date)
                    # Cancelling contract
                    contract.state = 'cancel' if contract.state == "open" else\
                        contract.state
                # Changing state of the employee if resigning today
                if (resignation.expected_revealing_date <= fields.Date.today()
                        and resignation.employee_id.active):
                    resignation.employee_id.active = False
                    # Changing fields in the employee table
                    # with respect to resignation
                    resignation.employee_id.resign_date = (
                        resignation.expected_revealing_date)
                    if resignation.resignation_type == 'resigned':
                        resignation.employee_id.resigned = True
                    else:
                        resignation.employee_id.fired = True
                    # Removing and deactivating user
                    if resignation.employee_id.user_id:
                        resignation.employee_id.user_id.active = False
                        resignation.employee_id.user_id = None
            else:
                raise ValidationError(_('Please Enter Valid Dates.'))

    def update_employee_status(self):
        resignation = self.env['hr.resignation'].search(
            [('state', '=', 'approved')])
        for rec in resignation:
            if rec.expected_revealing_date <= fields.Date.today():
                if rec.employee_id.active:
                    rec.employee_id.active = False

                # Changing fields in the employee  table with
                # respect to resignation
                rec.employee_id.resign_date = rec.expected_revealing_date
                if rec.resignation_type == 'resigned':
                    rec.employee_id.resigned = True
                    departure_reason_id = self.env[
                        'hr.departure.reason'].search(
                        [('name', '=', 'Resigned')])
                else:
                    rec.employee_id.fired = True
                    departure_reason_id = self.env[
                        'hr.departure.reason'].search(
                        [('name', '=', 'Fired')])

                today = fields.Date.today()
                running_contract_ids = self.env['hr.contract'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('company_id', '=', rec.employee_id.company_id.id),
                    ('state', '=', 'open'),
                ]).filtered(lambda c: c.date_start <= today and (
                        not c.date_end or c.date_end >= today))
                running_contract_ids.state = 'close'
                rec.employee_id.departure_reason_id = departure_reason_id
                rec.employee_id.departure_date = rec.approved_revealing_date

                # Removing and deactivating user
                if rec.employee_id.user_id:
                    rec.employee_id.user_id.active = False
                    rec.employee_id.user_id = None

