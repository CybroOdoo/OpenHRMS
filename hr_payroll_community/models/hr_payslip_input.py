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


class HrPayslipInput(models.Model):
    """Create new model for adding fields"""

    _name = "hr.payslip.input"
    _description = "Payslip Input"
    _order = "payslip_id, sequence"

    name = fields.Char(
        string="Description",
        required=True,
        help="Description of the input.",
    )
    payslip_id = fields.Many2one(
        "hr.payslip",
        string="Pay Slip",
        required=True,
        help="Payslip related to this input.",
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(
        required=True,
        index=True,
        default=10,
        help="Sequence to identify the record",
    )
    code = fields.Char(
        required=True, help="The code that can be used in the salary rules"
    )
    date_from = fields.Date(
        help="Starting date for the input line.",
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_to = fields.Date(
        help="Ending date for the input line.",
        required=True,
        default=lambda self: (
            fields.Date.today() + relativedelta(months=1, day=1, days=-1)
        ),
    )
    amount = fields.Float(
        help="It is used in computation. "
        "For e.g. A rule for sales having "
        "1% commission of basic salary for "
        "per product can defined in "
        "expression like result = "
        "inputs.SALEURO.amount * contract.wage*0.01."
    )
    contract_id = fields.Many2one(
        "hr.version",
        required=True,
        help="The contract to which this input applies.",
    )
