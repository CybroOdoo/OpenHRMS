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
from odoo import api, fields, models


class AccConfig(models.TransientModel):
    """ Added boolean fields which can approve loan by enabling True"""
    _inherit = 'res.config.settings'

    loan_approve = fields.Boolean(default=False,
                                  string="Approval from Accounting Department",
                                  config_parameter='ohrms_loan_accounting.loan_approve',
                                  help="Loan Approval from account manager")
    loan_approval_threshold = fields.Float(
        string="Approval Threshold",
        default=0.0,
        config_parameter='ohrms_loan_accounting.loan_approval_threshold',
        help="Loans with an amount equal to or above this threshold will require Account Manager approval if double approval is enabled."
    )
