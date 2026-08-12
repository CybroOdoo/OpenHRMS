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
from odoo.exceptions import ValidationError


class HrResignation(models.Model):
    """ Model for HR Resignations. This model is used to track employee
        resignations."""
    _name = 'hr.resignation'
    _description = 'HR Resignation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
                                      tracking=True)
    approved_revealing_date = fields.Date(
        string="Approved Last Day Of Employee",
        help='Date on which the request is confirmed by the manager.',
        tracking=True)
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
    notice_period = fields.Integer(string="Notice Period",
                                   help="Notice Period of the employee in days")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'),
         ('manager_approved', 'Manager Approved'),
         ('approved', 'Approved'),
         ('clearance', 'Clearance'),
         ('settlement', 'Settlement'),
         ('relieved', 'Relieved'),
         ('cancel', 'Rejected')],
        string='Status', default='draft', tracking=True)

    change_employee = fields.Boolean(string="Change Employee",
                                     compute="_compute_change_employee",
                                     help="Checks , if the user has permission"
                                          " to change the employee")
    is_manager = fields.Boolean(compute='_compute_is_manager', string="Is Manager")
    employee_contract = fields.Char(
        string="Contract Template",
        help="Current Contract of the employee"
    )

    # Process Fields
    clearance_line_ids = fields.One2many('hr.resignation.clearance.line', 'resignation_id', string='Clearance Lines')
    clearance_progress = fields.Float(string='Clearance Progress', compute='_compute_clearance_progress')
    settlement_state = fields.Selection([('draft', 'Draft'), ('computed', 'Computed'), ('approved', 'Approved')],
                                        string='Settlement State', default='draft')
    survey_id = fields.Many2one('survey.survey', string='Exit Interview Template')
    exit_interview_id = fields.Many2one('survey.user_input', string='Exit Interview')
    relieving_date = fields.Date(string='Relieving Date')

    # Analytics Fields
    reason_category_id = fields.Many2one('hr.departure.reason', string='Reason Category')
    replacement_employee_id = fields.Many2one('hr.employee', string='Replacement Employee')
    handover_notes = fields.Text(string='Handover Notes')

    # Settlement Fields
    pending_salary = fields.Float(string='Pending Salary')
    loan_recovery = fields.Float(string='Loan Recovery')
    advance_recovery = fields.Float(string='Advance Recovery')
    asset_recovery = fields.Float(string='Asset Recovery', compute='_compute_asset_recovery', store=True)
    net_settlement = fields.Float(string='Net Settlement', compute='_compute_net_settlement')
    settlement_date = fields.Date(string='Settlement Date', compute='_compute_default_settlement_date', store=True,
                                  readonly=False, tracking=True)
    is_settlement_date_reached = fields.Boolean(compute='_compute_is_settlement_date_reached')
    payslip_id = fields.Many2one('hr.payslip', string='Settlement Payslip')

    @api.depends('employee_id')
    def _compute_change_employee(self):
        """ Check whether the user has the permission to change the employee"""
        res_user = self.env.user
        self.change_employee = res_user.has_group('hr.group_hr_user')

    @api.depends('employee_id.parent_id.user_id')
    def _compute_is_manager(self):
        """ Compute if the current user is the manager of the resigning employee. """
        for rec in self:
            rec.is_manager = (rec.employee_id.parent_id.user_id == self.env.user) or self.env.user.has_group(
                'hr.group_hr_user')

    @api.constrains('employee_id')
    def _check_employee_id(self):
        """ Constraint method to check if the current user has the permission
             to create a resignation request for the specified employee.
        """
        for resignation in self:
            if not self.env.user.has_group('hr.group_hr_user'):
                if (resignation.employee_id.user_id.id and
                        resignation.employee_id.user_id.id != self.env.uid):
                    raise ValidationError(
                        _('You cannot create a request for other employees'))

    @api.constrains('employee_id', 'state')
    def _check_joined_date(self):
        """ Check if there is an active resignation request for the
            same employee in progress."""
        for resignation in self:
            if resignation.state not in ['cancel', 'relieved']:
                resignation_request = self.env['hr.resignation'].search(
                    [('employee_id', '=', resignation.employee_id.id),
                     ('state', 'not in', ['cancel', 'relieved']),
                     ('id', '!=', resignation.id)], limit=1)
                if resignation_request:
                    raise ValidationError(
                        _('There is already an active resignation request in progress for this employee!'))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Fetch notice period and contract details when employee is selected."""
        today = fields.Date.today()
        for rec in self:
            rec.joined_date = rec.employee_id.joining_date if rec.employee_id else False
            rec.employee_contract = False
            rec.notice_period = 0

            if rec.employee_id:
                contract = self.env['hr.version'].sudo().search([
                    ('employee_id', '=', rec.employee_id.id),
                    '|', ('date_start', '=', False),
                    ('date_start', '<=', today),
                    '|', ('date_end', '=', False),
                    ('date_end', '>=', today),
                ], limit=1)

                if contract:
                    rec.employee_contract = contract.contract_template_id.name
                    rec.notice_period = contract.notice_days

    @api.depends('clearance_line_ids', 'clearance_line_ids.state')
    def _compute_clearance_progress(self):
        """ Compute the progress percentage of the clearance checklist. """
        for rec in self:
            total = len(rec.clearance_line_ids)
            cleared = len(rec.clearance_line_ids.filtered(lambda l: l.state == 'cleared'))
            rec.clearance_progress = (cleared / total * 100.0) if total > 0 else 100.0

    @api.depends('pending_salary', 'loan_recovery', 'advance_recovery', 'asset_recovery')
    def _compute_net_settlement(self):
        """ Compute the net settlement amount by combining gross, deductions, and recoveries. """
        for rec in self:
            rec.net_settlement = rec.pending_salary - (rec.loan_recovery + rec.advance_recovery + rec.asset_recovery)

    @api.depends('clearance_line_ids', 'clearance_line_ids.due_amount')
    def _compute_asset_recovery(self):
        """ Compute the total asset recovery amount from blocked clearance lines with dues. """
        for rec in self:
            rec.asset_recovery = sum(rec.clearance_line_ids.mapped('due_amount'))

    @api.depends('expected_revealing_date')
    def _compute_default_settlement_date(self):
        """ Set the default settlement date to the current date. """
        for rec in self:
            if not rec.settlement_date:
                rec.settlement_date = rec.expected_revealing_date

    @api.depends('settlement_date')
    def _compute_is_settlement_date_reached(self):
        """ Check if the approved revealing date has passed to allow settlement computation. """
        today = fields.Date.today()
        for rec in self:
            rec.is_settlement_date_reached = bool(rec.settlement_date and rec.settlement_date <= today)

    @api.model
    def create(self, vals):
        """Override create to assign a sequence for the record(s)."""
        if isinstance(vals, list):  # multiple records
            for v in vals:
                if v.get('name', _('New')) == _('New'):
                    v['name'] = self.env['ir.sequence'].next_by_code(
                        'hr.resignation') or _('New')
        else:  # single record
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.resignation') or _('New')

        return super(HrResignation, self).create(vals)

    def action_confirm_resignation(self):
        """ Method triggered by the 'Confirm' button to confirm the
        resignation request."""
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
            if self.env.company.sudo().enable_manager_approval:
                resignation.state = 'confirm'
                manager = resignation.sudo().employee_id.parent_id
                if manager and manager.user_id:
                    resignation.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=manager.user_id.id,
                        summary=_('Review resignation request'),
                        note=_('Please review the resignation request for %s.') % resignation.employee_id.name
                    )
            else:
                resignation.state = 'manager_approved'
            resignation.resign_confirm_date = fields.Date.today()
            if resignation.expected_revealing_date and resignation.expected_revealing_date > fields.Date.today():
                resignation.approved_revealing_date = resignation.expected_revealing_date + timedelta(days=resignation.notice_period)
            else:
                resignation.approved_revealing_date = resignation.resign_confirm_date + timedelta(days=resignation.notice_period)

    def action_manager_approve(self):
        """ Method triggered by the Line Manager to approve the resignation."""
        for resignation in self:
            resignation.state = 'manager_approved'

    def action_cancel_resignation(self):
        """ Method triggered by the 'Cancel' button to cancel the resignation
            request."""
        for resignation in self:
            resignation.state = 'cancel'

    def action_reject_resignation(self):
        """ Method triggered by the 'Reject' button to reject the
            resignation request."""
        for resignation in self:
            resignation.state = 'cancel'

    def action_reset_to_draft(self):
        """ Method triggered by the 'Set to Draft' button to reset the
        resignation request to the 'draft' state."""
        for resignation in self:
            resignation.state = 'draft'
            resignation.employee_id.active = True
            resignation.employee_id.resigned = False
            resignation.employee_id.fired = False

    def action_approve_resignation(self):
        """ Method triggered by the 'Approve' button to
               approve the resignation."""
        for resignation in self:
            if (resignation.expected_revealing_date and
                    resignation.resign_confirm_date):
                employee_contract = self.env['hr.version'].sudo().search(
                    [('employee_id', '=', resignation.employee_id.id)])
                if not employee_contract:
                    raise ValidationError(
                        _("There are no Contracts found for this employee"))
                for contract in employee_contract:
                    resignation.state = 'clearance'

                # Generate clearance lines from template
                template = self.env.company.clearance_template_id
                if template:
                    for c_type in template.clearance_type_ids:
                        clearance_line = self.env['hr.resignation.clearance.line'].create({
                            'resignation_id': resignation.id,
                            'clearance_type_id': c_type.id,
                            'responsible_user_id': c_type.default_responsible_id.id or self.env.uid,
                        })
                        if clearance_line.responsible_user_id:
                            resignation.activity_schedule(
                                'mail.mail_activity_data_todo',
                                user_id=clearance_line.responsible_user_id.id,
                                summary=_('Clearance Check'),
                                note=_('Please review the clearance checklist for %s.') % resignation.employee_id.name
                            )

                # Check for open custodies
                resignation._check_open_custody()
            else:
                raise ValidationError(_('Please Enter Valid Dates.'))

    def _check_open_custody(self):
        """ Check if the employee has any unreturned custody assets and automatically create blocked clearance lines. """
        for resignation in self:
            open_custodies = self.env['hr.custody'].search([
                ('employee_id', '=', resignation.employee_id.id),
                ('state', '=', 'approved')
            ])
            if open_custodies:
                remarks = "Pending return:\n" + "\n".join(
                    [f"- {c.custody_property_id.name} ({c.name})" for c in open_custodies])
                # Find IT/Admin clearance line to block
                admin_lines = resignation.clearance_line_ids.filtered(
                    lambda l: l.clearance_type_id.name in ['IT', 'Admin'])
                if admin_lines:
                    for line in admin_lines:
                        line.state = 'blocked'
                        if line.remarks:
                            line.remarks += "\n\n" + remarks
                        else:
                            line.remarks = remarks
                else:
                    # Create a Custody Recovery clearance line if no Admin/IT lines exist
                    c_type = self.env['hr.clearance.type'].search([('name', 'in', ['IT', 'Admin', 'Custody Recovery'])],
                                                                  limit=1)
                    if not c_type:
                        c_type = self.env['hr.clearance.type'].sudo().create({
                            'name': 'Custody Recovery',
                            'default_responsible_id': self.env.uid,
                        })
                    self.env['hr.resignation.clearance.line'].sudo().create({
                        'resignation_id': resignation.id,
                        'clearance_type_id': c_type.id,
                        'responsible_user_id': c_type.default_responsible_id.id or self.env.uid,
                        'state': 'blocked',
                        'remarks': remarks
                    })

    def action_compute_settlement(self):
        """ Compute the final settlement amount including pending salary, loans, and advances. """
        for resignation in self:
            advance_recovery = 0.0
            loan_recovery = 0.0

            # Fetch Salary Advance (Approved advances for the revealing month)
            if 'salary.advance' in self.env and resignation.employee_id:
                target_date = resignation.expected_revealing_date or fields.Date.today()
                advances = self.env['salary.advance'].search([
                    ('employee_id', '=', resignation.employee_id.id),
                    ('state', '=', 'approve'),
                ])
                advance_recovery = sum(a.advance for a in advances if
                                       a.date.month == target_date.month and a.date.year == target_date.year)

            # Fetch Loan (All approved loans with an open balance)
            if 'hr.loan' in self.env and resignation.employee_id:
                loans = self.env['hr.loan'].search([
                    ('employee_id', '=', resignation.employee_id.id),
                    ('state', '=', 'approve'),
                    ('balance_amount', '>', 0)
                ])
                loan_recovery = sum(loans.mapped('balance_amount'))

            resignation.advance_recovery = advance_recovery
            resignation.loan_recovery = loan_recovery
            resignation.settlement_state = 'computed'

    def action_approve_settlement(self):
        """ Approve the final settlement computation and mark the state as settlement. """
        for resignation in self:
            if resignation.clearance_progress < 100.0:
                raise ValidationError(_("Cannot approve settlement until all clearance lines are cleared!"))

            # Payroll Integration: Create a Payslip for the final settlement
            date_to = resignation.settlement_date or resignation.expected_revealing_date or fields.Date.today()
            date_from = date_to.replace(day=1)

            Payslip = self.env['hr.payslip'].sudo()

            # Find a contract first
            contract_ids = Payslip.get_contract(resignation.employee_id, date_from, date_to)
            contract_id = contract_ids[0] if contract_ids else False

            if not contract_id:
                # Fallback to the latest contract
                fallback_contract = self.env['hr.version'].search([
                    ('employee_id', '=', resignation.employee_id.id)
                ], order='date_version desc', limit=1)
                contract_id = fallback_contract.id if fallback_contract else False

            if not contract_id:
                raise ValidationError(
                    _("No contract found for employee %s. A contract is required to generate a payslip.") % resignation.employee_id.name)

            # Fetch default payslip values with the explicit contract
            defaults = \
            Payslip.with_context(contract=True).onchange_employee_id(date_from, date_to, resignation.employee_id.id,
                                                                     contract_id=contract_id)['value']

            # Convert raw dicts from onchange to ORM commands
            worked_days_lines = []
            for wd in defaults.get('worked_days_line_ids', []):
                worked_days_lines.append((0, 0, wd) if isinstance(wd, dict) else wd)

            input_lines = []
            for il in defaults.get('input_line_ids', []):
                input_lines.append((0, 0, il) if isinstance(il, dict) else il)

            payslip_vals = {
                'employee_id': resignation.employee_id.id,
                'name': defaults.get('name', f"F&F Settlement - {resignation.employee_id.name}"),
                'date_from': date_from,
                'date_to': date_to,
                'contract_id': contract_id,
                'struct_id': defaults.get('struct_id'),
                'company_id': defaults.get('company_id', self.env.company.id),
                'worked_days_line_ids': worked_days_lines,
                'input_line_ids': input_lines,
            }

            payslip = Payslip.create(payslip_vals)
            payslip.action_compute_sheet()

            resignation.payslip_id = payslip.id
            resignation.state = 'settlement'
            resignation.settlement_state = 'approved'

    def action_relieve(self):
        """ Relieve the employee by deactivating their user and employee records. """
        for resignation in self:
            if resignation.state != 'settlement' or resignation.settlement_state != 'approved':
                raise ValidationError(_("Clearance and Settlement must be completed before relieving."))

            resignation.state = 'relieved'
            resignation.relieving_date = fields.Date.today()

            # Deactivate employee
            resignation.employee_id.active = False
            resignation.employee_id.resign_date = resignation.expected_revealing_date

            if resignation.reason_category_id.name == 'Resigned':
                resignation.employee_id.resigned = True
            elif resignation.reason_category_id.name == 'Fired':
                resignation.employee_id.fired = True

            departure_reason_id = resignation.reason_category_id

            resignation.employee_id.departure_reason_id = departure_reason_id
            resignation.employee_id.departure_date = resignation.relieving_date

            if resignation.employee_id.user_id:
                resignation.employee_id.user_id.active = False
                resignation.employee_id.user_id = None

    def action_withdraw(self):
        """ Withdraw the resignation request if the employee decides to stay. """
        for resignation in self:
            if resignation.state == 'relieved':
                raise ValidationError(_("Cannot withdraw a resignation that is already relieved."))
            resignation.state = 'cancel'
            resignation.employee_id.active = True
            resignation.employee_id.resigned = False
            resignation.employee_id.fired = False

    @api.model
    def update_employee_status(self):
        """ Periodic cron job method to relieve employees who have reached their approved last date. """
        today = fields.Date.today()
        resignations = self.search([
            ('state', '=', 'settlement'),
            ('settlement_state', '=', 'approved'),
            ('expected_revealing_date', '<=', today)
        ])
        for resignation in resignations:
            resignation.action_relieve()

    def action_send_exit_interview(self):
        """ Open a wizard to send the selected exit interview survey to the resigning employee. """
        self.ensure_one()

        partner = self.employee_id.user_id.partner_id or self.employee_id.work_contact_id
        if not partner:
            if self.employee_id.work_email:
                # If they have a work email but no partner, try to find or create one
                partner = self.env['res.partner'].search([('email', '=', self.employee_id.work_email)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].sudo().create({
                        'name': self.employee_id.name,
                        'email': self.employee_id.work_email,
                    })
            else:
                raise ValidationError(
                    _("The employee must have a linked user, private address, or work email to send an interview."))

        if not self.survey_id:
            raise ValidationError(_("Please select an Exit Interview Template before sending."))

        deadline = self.expected_revealing_date
        formatted_deadline = deadline.strftime('%b %d, %Y') if deadline else ''
        
        body = _("""
<div style="margin: 0px; padding: 0px; font-size: 13px;">
    <p style="margin: 0px; padding: 0px; font-size: 13px;">
        Dear %(name)s,<br/><br/>
        We are sorry to see you go! As part of our offboarding process, we would highly appreciate it if you could take a few minutes to complete our Exit Interview.<br/><br/>
        Your honest feedback is incredibly valuable to us and will help us improve our workplace for everyone.
        <div style="margin: 16px 0px 16px 0px;">
            <a t-att-href="(object.get_start_url())"
                t-attf-style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #FFFFFF; border-radius: 5px; font-size:13px;">
                Start Exit Interview
            </a>
        </div>
        %(deadline_text)s
        Thank you for your contributions, and we wish you all the best in your future endeavors!
    </p>
</div>
        """) % {
            'name': partner.name or 'Employee',
            'deadline_text': f"Please complete the survey before <strong>{formatted_deadline}</strong>.<br/><br/>" if formatted_deadline else "",
        }

        template = self.env.ref('hr_resignation.mail_template_resignation_exit_interview', raise_if_not_found=False)
        local_context = dict(
            default_partner_ids=partner.ids,
            default_survey_id=self.survey_id.id,
            default_template_id=template.id if template else False,
            default_email_layout_xmlid='mail.mail_notification_light',
            default_deadline=self.expected_revealing_date,
            default_body=body,
            force_send_survey=True,
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _("Send Exit Interview"),
            'view_mode': 'form',
            'res_model': 'survey.invite',
            'target': 'new',
            'context': local_context,
        }

    @api.model
    def _add_recovery_rules_to_structures(self):
        """Called via XML data to add the newly created recovery rules to all existing structures."""
        asset_rule = self.env.ref('hr_resignation.hr_salary_rule_asset_recovery', raise_if_not_found=False)

        if asset_rule:
            asset_rule.sudo().write({
                'condition_select': 'none',
                'amount_python_compute': "result = -(inputs.ASSET_REC.amount) if inputs.ASSET_REC else 0.0"
            })

        if asset_rule:
            structures = self.env['hr.payroll.structure'].search([])
            for struct in structures:
                struct.sudo().write({
                    'rule_ids': [(4, asset_rule.id)]
                })


class SurveyInvite(models.TransientModel):
    """
    Inherits survey.invite to link the sent survey directly back to the hr.resignation record.
    """
    _inherit = 'survey.invite'

    def _send_mail(self, answer):
        """Override to force send the email immediately if requested in context."""
        mail = super(SurveyInvite, self)._send_mail(answer)
        if self.env.context.get('force_send_survey'):
            mail.send()
        return mail
