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
"""Insurance Policy master data model."""
from odoo import fields, models


class InsurancePolicy(models.Model):
    """Model to manage insurance policies."""

    _name = 'insurance.policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Policies of Insurance"

    name = fields.Char(string='Name', required=True, help="Policy Name")
    insurer_id = fields.Many2one(
        'res.partner', string='Insurance Provider',
        help="Insurance company providing the policy",
    )
    group_policy_number = fields.Char(
        string='Group Policy Number',
        help="Reference number for the group policy",
    )
    note_field = fields.Html(
        string='Comment',
        help="Notes for the insurance policy if any",
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, help="Company",
        default=lambda self: self.env.company,
    )
    policy_coverage = fields.Selection([
        ('monthly', 'Monthly'),
        ('six_months', 'Semi Annual'),
        ('yearly', 'Annual'),
    ], default='monthly', string='Policy Coverage', help="Default duration of the policy")
    amount = fields.Float(string='Premium', help="Default Policy amount")
    sum_insured = fields.Float(string="Sum Insured", help="Default Insured sum")
    company_percentage = fields.Float(
        string='Company Percentage',
        help="Company contribution percentage",
    )
