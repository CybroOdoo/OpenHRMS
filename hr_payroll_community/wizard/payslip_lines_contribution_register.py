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
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class PayslipLinesContributionRegister(models.TransientModel):
    """Create new model Payslip Lines by Contribution Registers"""

    _name = "payslip.lines.contribution.register"
    _description = "Payslip Lines by Contribution Registers"

    date_from = fields.Date(
        help="Starting Date for Payslip Lines",
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_to = fields.Date(
        help="Ending Date for Payslip Lines",
        required=True,
        default=lambda self: (
            fields.Date.today() + relativedelta(months=1, day=1, days=-1)
        ),
    )

    def action_print_report(self):
        """Function for Print Report"""
        active_ids = self.env.context.get("active_ids", [])
        datas = {
            "ids": active_ids,
            "model": "hr.contribution.register",
            "form": self.read()[0],
        }
        return self.env.ref(
            "hr_payroll_community.contribution_register_action"
        ).report_action([], data=datas)
