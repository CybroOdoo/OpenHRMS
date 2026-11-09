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
"""Employee Insurance management model."""
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrInsurance(models.Model):
    """Model for managing employee insurance records."""

    _name = 'hr.insurance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Insurance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        required=True, help="Employee linked to this insurance", tracking=True,
    )
    policy_id = fields.Many2one(
        'insurance.policy',
        string='Policy', required=True, help="Selected insurance policy", tracking=True,
    )
    insurer_id = fields.Many2one(
        related='policy_id.insurer_id', string='Insurance Provider', readonly=True,
        help="Insurance company providing the policy",
    )
    group_policy_number = fields.Char(
        related='policy_id.group_policy_number', string='Group Policy Number', readonly=True,
        help="Reference number for the group policy",
    )
    amount = fields.Float(string='Premium', required=True, help="Policy amount", tracking=True)
    sum_insured = fields.Float(
        string="Sum Insured", required=True, help="Insured sum", tracking=True,
    )
    policy_coverage = fields.Selection([
        ('monthly', 'Monthly'),
        ('six_months', 'Semi Annual'),
        ('yearly', 'Annual'),
    ], required=True, string='Policy Coverage', help="Duration of the policy", tracking=True)
    is_deducted = fields.Boolean(
        "Lump-Sum Deducted", default=False, readonly=True, tracking=True,
        help="Indicates whether the deduction has been applied to a payslip",
    )
    date_from = fields.Date(
        string='Date From', default=fields.Date.context_today,
        help="Start date", tracking=True,
    )
    date_to = fields.Date(
        string='Date To', help="End date", tracking=True,
        compute='_compute_date_to', store=True, readonly=True,
    )
    company_percentage = fields.Float(
        string='Company Percentage', readonly=True,
        help="Percentage contributed by the company",
    )
    deducted_amount = fields.Float(
        string="Salary Deducted",
        compute="_compute_deducted_amount",
        help="Lump-sum amount that is deducted from the salary",
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='draft', string="State", help="State for the insurance", tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, help="Company",
        default=lambda self: self.env.company,
    )

    @api.depends('amount', 'company_percentage')
    def _compute_deducted_amount(self):
        """Compute the net lump-sum deduction amount from premium and company percentage."""
        for ins in self:
            if ins.amount:
                net_term_amount = ins.amount - ((ins.amount * ins.company_percentage) / 100)
                ins.deducted_amount = net_term_amount
            else:
                ins.deducted_amount = 0.0

    @api.depends('policy_coverage', 'date_from')
    def _compute_date_to(self):
        """Compute the end date of the policy based on the start date and coverage duration."""
        for rec in self:
            if rec.date_from and rec.policy_coverage:
                if rec.policy_coverage == 'monthly':
                    rec.date_to = rec.date_from + relativedelta(months=1, days=-1)
                elif rec.policy_coverage == 'six_months':
                    rec.date_to = rec.date_from + relativedelta(months=6, days=-1)
                elif rec.policy_coverage == 'yearly':
                    rec.date_to = rec.date_from + relativedelta(years=1, days=-1)
                else:
                    rec.date_to = False
            else:
                rec.date_to = False

    def action_renewal(self):
        """Action to renew an expired policy by updating the start date."""
        for rec in self:
            if rec.state == 'expired':
                rec.date_from = fields.Date.today()
                rec.is_deducted = False
                rec.state = 'active'
                rec._compute_status()

    def action_confirm(self):
        """Action to confirm the policy from draft to active."""
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'active'
                rec._compute_status()

    def _compute_status(self):
        """Update insurance record state based on current date and validity period."""
        current_date = fields.Date.today()
        for rec in self:
            if rec.date_from and rec.date_from <= current_date:
                if rec.date_to and rec.date_to >= current_date:
                    rec.state = 'active'
                else:
                    rec.state = 'expired'
            else:
                rec.state = 'active'

    @api.onchange('policy_id')
    def _onchange_policy_id(self):
        """Auto-populate insurance fields when a policy master is selected."""
        if self.policy_id:
            if self.policy_id.policy_coverage:
                self.policy_coverage = self.policy_id.policy_coverage
            if self.policy_id.amount:
                self.amount = self.policy_id.amount
            if self.policy_id.sum_insured:
                self.sum_insured = self.policy_id.sum_insured
            if self.policy_id.company_percentage:
                self.company_percentage = self.policy_id.company_percentage
            if not self.date_from:
                self.date_from = fields.Date.today()

    @api.model
    def _cron_update_insurance_status(self):
        """Cron job to update insurance status and schedule reminders."""
        active_policies = self.search([('state', '=', 'active')])
        for policy in active_policies:
            policy._compute_status()

        warning_date = fields.Date.today() + relativedelta(days=7)
        expiring_policies = self.search([
            ('state', '=', 'active'),
            ('date_to', '=', warning_date),
        ])

        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        for policy in expiring_policies:
            user_id = policy.employee_id.user_id.id or self.env.uid
            if activity_type:
                existing_activity = self.env['mail.activity'].search([
                    ('res_model', '=', self._name),
                    ('res_id', '=', policy.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('user_id', '=', user_id),
                ], limit=1)
                if not existing_activity:
                    policy.activity_schedule(
                        'mail.mail_activity_data_todo',
                        note='Insurance Policy is expiring in 7 days! Please review for renewal.',
                        user_id=user_id,
                    )
