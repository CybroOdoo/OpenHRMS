# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_multiple_loans = fields.Boolean(
        string="Allow Multiple Loans",
        config_parameter='ohrms_loan.allow_multiple_loans',
        help="Enable this to allow employees to have multiple active loans based on conditions"
    )

    multiple_loan_condition = fields.Selection([
        ('none', 'Disabled'),
        ('years_of_service', 'By Years of Service'),
        ('job_position', 'By Job Position'),
    ], string="Multiple Loan Condition",
        config_parameter='ohrms_loan.multiple_loan_condition',
        default='none',
        help="Select the condition to allow multiple loans")

    min_service_years = fields.Integer(
        string="Minimum Years of Service",
        config_parameter='ohrms_loan.min_service_years',
        default=2,
        help="Minimum years of service required for multiple loans"
    )

    allowed_job_ids = fields.Many2many(
        'hr.job',
        string="Allowed Job Positions",
        help="Job positions allowed to have multiple loans"
    )

    @api.onchange('allow_multiple_loans')
    def _onchange_allow_multiple_loans(self):
        if not self.allow_multiple_loans:
            self.multiple_loan_condition = 'none'

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        allowed_jobs = self.env['ir.config_parameter'].sudo().get_param(
            'ohrms_loan.allowed_job_ids', ''
        )
        if allowed_jobs:
            job_ids = [int(x) for x in allowed_jobs.split(',') if x.strip().isdigit()]
            res.update(allowed_job_ids=[(6, 0, job_ids)])

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            'ohrms_loan.allowed_job_ids',
            ','.join(map(str, self.allowed_job_ids.ids))
        )
