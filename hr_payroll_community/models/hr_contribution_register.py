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
from odoo import fields, models


class HrContributionRegister(models.Model):
    """Create a new model for adding fields."""

    _name = "hr.contribution.register"
    _description = "Contribution Register"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company.id
    )
    partner_id = fields.Many2one(
        "res.partner", help="Third-party partner involved in the contribution."
    )
    name = fields.Char(
        required=True, help="Name of the contribution register."
    )
    register_line_ids = fields.One2many(
        "hr.payslip.line",
        "register_id",
        readonly=True,
        help="Payslip lines associated with this register.",
    )
    note = fields.Text(
        string="Description", help="Description of the contribution register."
    )
