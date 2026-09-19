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
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    """Create new model for getting Payslip Batches"""
    _name = 'hr.payslip.run'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payslip Batches'

    name = fields.Char(required=True, help="Name for Payslip Batches",
                       string="Name", tracking=True)
    slip_ids = fields.One2many('hr.payslip',
                               'payslip_run_id',
                               string='Payslips',
                               help="Choose Payslips for Batches")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Validated'),
        ('paid', 'Paid'),
        ('cancel', 'Canceled'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft', tracking=True,
                               help="Status for Payslip Batches")
    date_start = fields.Date(string='Date From', required=True,
                             help="start date for batch",
                             default=lambda self: fields.Date.to_string(
                                 date.today().replace(day=1)))
    date_end = fields.Date(string='Date To', required=True,
                           help="End date for batch",
                           default=lambda self: fields.Date.to_string(
                               (datetime.now() + relativedelta(months=+1, day=1,
                                                               days=-1)).date())
                           )
    credit_note = fields.Boolean(string='Credit Note', default=False,
                                 help="If its checked, indicates that all"
                                      "payslips generated from here are refund"
                                      "payslips.")
    company_id = fields.Many2one('res.company', string='Company',
                                 copy=False, readonly=True,
                                 help="Company of the payslip.",
                                 default=lambda self: self.env.user.company_id)

    def action_payslip_run(self):
        """Function for state change and resetting payslips"""
        for run in self:
            for slip in run.slip_ids:
                # this action is also reachable from a 'paid' batch (see the
                # "Set to Draft" button's visibility), so paid payslips need
                # the same unwind-then-reset treatment as done ones -- missing
                # that left a paid slip untouched while its batch flipped to
                # draft around it, an inconsistent state.
                if slip.state in ('done', 'paid'):
                    slip.action_payslip_cancel()
                if slip.state in ('cancel', 'done', 'paid'):
                    slip.action_payslip_draft()
        return self.write({'state': 'draft'})

    def action_confirm_payslips(self):
        """Confirm all draft payslips in the batch"""
        for run in self:
            if not run.slip_ids:
                raise UserError(_("You must generate or add payslips before confirming the batch."))
            draft_slips = run.mapped('slip_ids').filtered(lambda slip: slip.state == 'draft')
            for slip in draft_slips:
                slip.action_payslip_done()
            run.write({'state': 'done'})

    def action_cancel_payslips(self):
        """Cancel all payslips in the batch and set batch to cancel"""
        for run in self:
            for slip in run.slip_ids:
                slip.action_payslip_cancel()
            run.write({'state': 'cancel'})


    def action_mark_as_paid(self):
        """Mark batch and its payslips as paid"""
        for run in self:
            for slip in run.slip_ids.filtered(lambda s: s.state == 'done'):
                slip.action_mark_as_paid()
            run.write({'state': 'paid'})
        return True
