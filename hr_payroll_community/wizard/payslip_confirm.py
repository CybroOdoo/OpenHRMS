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
from odoo import models

class PayslipConfirm(models.TransientModel):
    """Create a new model for getting mass confirm wizard"""
    _name = 'payslip.confirm'
    _description = 'Mass Confirm Payslip'

    def confirm_payslip(self):
        """Mass Confirmation of Payslip"""
        record_ids = self.env.context.get('active_ids', [])
        for each in record_ids:
            # only draft payslips are eligible for confirmation -- 'done' is
            # already confirmed, 'cancel' is voided, and 'paid' must never be
            # re-run through action_payslip_done() (it recomputes the sheet
            # from scratch and would revert an already-paid payslip back to
            # 'done' with a brand new set of lines, silently rewriting a
            # financial record that's already been paid out).
            payslip_id = self.env['hr.payslip'].search([('id', '=', each),
                                                        ('state', '=', 'draft')])
            if payslip_id:
                payslip_id.action_payslip_done()
