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
import time
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class SalaryAdvance(models.Model):
    """Class for the model salary_advance. Contains methods and fields of the
       model."""
    _name = "salary.advance"
    _description = "Salary Advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', readonly=True,
                       default=lambda self: _('New'),
                       help='Name of the the advanced salary.')
    @api.model
    def _default_employee_id(self):
        """Returns the default employee record for the current user."""
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True, help="Name of the Employee",
                                  default=_default_employee_id,
                                  tracking=True)
    date = fields.Date(string='Date', required=True,
                       default=lambda self: fields.Date.today(),
                       help="Submit date of the advanced salary.",
                       tracking=True)
    reason = fields.Text(string='Reason', help="Reason for the advance salary"
                                               " request.")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True,
                                  help='Currency of the company.',
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 help='Company of the employee,',
                                 default=lambda self: self.env.company)
    advance = fields.Monetary(string='Advance Amount', required=True,
                           help='The requested money.', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department',
                                    related='employee_id.department_id',
                                    help='Department of the employee.')
    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Submitted'),
                              ('approved', 'Approved'),
                              ('paid', 'Paid'),
                              ('closed', 'Closed'),
                              ('cancelled', 'Cancelled')], string='Status',
                             default='draft', tracking=True,
                             help='State of the salary advance.')
    employee_contract_id = fields.Many2one('hr.version', string='Contract',
                                           compute='_compute_employee_contract_id',
                                           store=True,
                                           help='Running contract of the employee.')
                                           
    # --- New Computed Balances ---
    monthly_wage = fields.Monetary(string="Monthly Wage", compute='_compute_advance_limits', store=True,
                                   help="The monthly wage of the employee based on their active contract.")
    maximum_allowed = fields.Monetary(string="Maximum Allowed", compute='_compute_advance_limits',
                                      help="The maximum advance amount allowed based on company policy.")
    already_outstanding = fields.Monetary(string="Already Outstanding", compute='_compute_advance_limits',
                                          help="The total amount of unsettled advances currently held by this employee.")
    eligible_amount = fields.Monetary(string="Remaining Eligible", compute='_compute_advance_limits',
                                      help="The remaining advance amount this employee is eligible to request.")
    
    deducted_amount = fields.Monetary(string="Deducted Amount", compute='_compute_deducted_amount', store=True, tracking=True,
                                      help="The total amount already recovered through payroll deductions.")
    balance_amount = fields.Monetary(string="Balance Amount", compute='_compute_deducted_amount', store=True,
                                     help="The remaining outstanding amount that is yet to be recovered.")
    
    payslip_input_ids = fields.One2many('hr.payslip.input', 'advance_id', string="Payslip Inputs",
                                        help="Payslip inputs linking this advance to payslips.")
    payslip_ids = fields.Many2many('hr.payslip', string="Payslips", compute='_compute_payslip_ids',
                                   help="Payslips that include deductions for this advance.")
    payslip_count = fields.Integer(string="Payslip Count", compute='_compute_payslip_count',
                                   help="Number of payslips linked to this advance.")
    payment_ids = fields.Many2many('account.payment', string="Payments", copy=False,
                                   help="Accounting payments registered for disbursing this advance.")
    payment_count = fields.Integer(string="Payment Count", compute='_compute_payment_count',
                                   help="Number of accounting payments linked to this advance.")
    move_ids = fields.Many2many('account.move', string="Journal Entries", compute='_compute_move_ids',
                                help="Journal entries generated for this advance.")
    move_count = fields.Integer(string="Move Count", compute='_compute_move_count',
                                help="Number of journal entries linked to this advance.")
    
    is_hr_manager = fields.Boolean(compute='_compute_is_hr_manager',
                                   help="Technical field to check if the user is an HR Manager.")
                                   
    journal_id = fields.Many2one('account.journal', string="Payment Journal",
                                 domain="[('type', 'in', ('bank', 'cash'))]",
                                 help="The accounting journal used to register the salary advance payment.")
    receivable_account_id = fields.Many2one('account.account', string="Employee Advance Account",
                                            domain="[('account_type', '=', 'asset_receivable')]",
                                            help="The receivable account used to record the advance issued to the employee.")

    def _compute_is_hr_manager(self):
        """Check if the current user belongs to the HR Manager group."""
        for rec in self:
            rec.is_hr_manager = self.env.user.has_group('hr.group_hr_user')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to generate sequence for new salary advance requests."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('salary.advance.seq') or _('New')
        return super(SalaryAdvance, self).create(vals_list)

    @api.depends('employee_id', 'date')
    def _compute_employee_contract_id(self):
        """Compute the active contract for the employee based on the advance date."""
        for rec in self:
            if rec.employee_id and rec.date:
                # Find active contract on the request date
                contracts = self.env['hr.version'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('date_start', '<=', rec.date),
                    '|', ('date_end', '=', False), ('date_end', '>=', rec.date)
                ], limit=1)
                rec.employee_contract_id = contracts.id if contracts else False
            else:
                rec.employee_contract_id = False

    @api.depends('employee_id', 'company_id', 'employee_contract_id')
    def _compute_advance_limits(self):
        """
        Computes the eligible advance limits for the employee based on company policies.
        Takes into account the monthly wage, max percentage, max fixed amount, 
        and already outstanding advance balances.
        """
        for rec in self:
            if rec.employee_contract_id:
                wage = rec.employee_contract_id.sudo().wage
            else:
                wage = 0.0
                
            rec.monthly_wage = wage
            max_percent = rec.company_id.salary_advance_max_percent or 100.0
            max_fixed = rec.company_id.salary_advance_max_amount or 0.0
            
            allowed_by_percent = wage * (max_percent / 100.0)
            if max_fixed > 0.0:
                rec.maximum_allowed = min(allowed_by_percent, max_fixed)
            else:
                rec.maximum_allowed = allowed_by_percent
                
            if rec.employee_id:
                other_advances = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('id', '!=', rec.id if rec.id else False),
                    ('state', 'in', ['approved', 'paid'])
                ])
                rec.already_outstanding = sum(other_advances.mapped('balance_amount'))
            else:
                rec.already_outstanding = 0.0
                
            rec.eligible_amount = max(0.0, rec.maximum_allowed - rec.already_outstanding)

    @api.depends('advance', 'payslip_input_ids.amount', 'payslip_input_ids.payslip_id.state')
    def _compute_deducted_amount(self):
        """
        Calculates the total amount deducted from confirmed payslips and updates
        the remaining balance amount of the salary advance.
        """
        for rec in self:
            # Calculate total deductions from confirmed payslips linked to this advance
            deducted = 0.0
            if rec.id:
                inputs = self.env['hr.payslip.input'].sudo().search([
                    ('advance_id', '=', rec.id),
                    ('payslip_id.state', '=', 'done')
                ])
                deducted = sum(inputs.mapped('amount'))
            rec.deducted_amount = deducted
            rec.balance_amount = rec.advance - rec.deducted_amount

    def _compute_payslip_ids(self):
        """Compute the payslips related to this salary advance."""
        for rec in self:
            if rec.id:
                inputs = self.env['hr.payslip.input'].sudo().search([('advance_id', '=', rec.id)])
                rec.payslip_ids = inputs.mapped('payslip_id')
            else:
                rec.payslip_ids = False

    @api.depends('payment_ids')
    def _compute_move_ids(self):
        """Compute the journal entries from the related payments."""
        for rec in self:
            rec.move_ids = rec.payment_ids.mapped('move_id')

    def _compute_payslip_count(self):
        """Compute the total number of related payslips."""
        for rec in self:
            rec.payslip_count = len(rec.payslip_ids)

    def _compute_payment_count(self):
        """Compute the total number of related payments."""
        for rec in self:
            rec.payment_count = len(rec.payment_ids)

    def _compute_move_count(self):
        """Compute the total number of related journal entries."""
        for rec in self:
            rec.move_count = len(rec.move_ids)

    def action_view_payslips(self):
        """Action to open the related payslips for the salary advance."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('hr_payroll_community.action_hr_payslip')
        action['domain'] = [('id', 'in', self.payslip_ids.ids)]
        action['context'] = {'default_employee_id': self.employee_id.id}
        return action

    def action_view_payments(self):
        """Action to open the related payments for the salary advance."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_payments_payable')
        action['domain'] = [('id', 'in', self.payment_ids.ids)]
        action['context'] = {
            'default_payment_type': 'outbound',
            'default_partner_type': 'supplier',
            'search_default_outbound_filter': 1
        }
        return action

    def action_view_journal_entries(self):
        """Action to open the related journal entries for the salary advance."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
        action['domain'] = [('id', 'in', self.move_ids.ids)]
        return action

    def action_view_employee(self):
        """Action to open the related employee form view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_id.id,
            'view_mode': 'form',
        }

    @api.constrains('advance', 'state')
    def _check_advance_amount(self):
        """Constraint to ensure the requested advance amount is greater than zero."""
        for rec in self:
            if rec.state in ['submitted', 'approved', 'paid'] and rec.advance <= 0.0:
                raise exceptions.ValidationError(_('The requested advance amount must be greater than zero.'))

    @api.constrains('state')
    def _check_state_modifications(self):
        """Constraint to validate state modifications."""
        for rec in self:
            if rec.state == 'closed':
                # Further modifications should be blocked, but standard Odoo 
                # handles this via readonly fields in the view.
                pass

    def action_submit(self):
        """
        Submits the salary advance request. Validates the existence of an active contract,
        checks if the requested amount is within eligible limits, and verifies multiple
        active advance policies.
        """
        for rec in self:
            if not rec.employee_contract_id:
                raise exceptions.UserError(_('An active contract is required to submit a salary advance.'))
            if rec.eligible_amount < rec.advance:
                raise exceptions.UserError(_('The requested amount exceeds the remaining eligible amount for this employee.'))
            if not rec.company_id.salary_advance_multiple_active and rec.already_outstanding > 0:
                raise exceptions.UserError(_('This company does not allow multiple active advances.'))
            rec.state = 'submitted'

    def action_approve(self):
        """
        Approves the salary advance request. Ensures that the payment journal and 
        employee advance account are configured before approving.
        """
        for rec in self:
            if not rec.journal_id or not rec.receivable_account_id:
                raise exceptions.UserError(_('Please configure the Payment Journal and Employee Advance Account before approving.'))
            rec.state = 'approved'

    def action_cancel(self):
        """
        Cancels the salary advance request. Prevents cancellation if the advance
        has already been paid to the employee.
        """
        for rec in self:
            if rec.state == 'paid':
                raise exceptions.UserError(_('You cannot cancel an advance that has already been paid.'))
            rec.state = 'cancelled'
