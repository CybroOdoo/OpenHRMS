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
from odoo.exceptions import UserError


class HrPayslipLine(models.Model):
    """Create new model for adding Payslip Line"""

    _name = "hr.payslip.line"
    _description = "Payslip Line"
    _inherit = "hr.salary.rule"
    _order = "contract_id, sequence"

    slip_id = fields.Many2one(
        "hr.payslip",
        string="Pay Slip",
        required=True,
        ondelete="cascade",
        help="Payslip associated with this line.",
    )
    salary_rule_id = fields.Many2one(
        "hr.salary.rule",
        string="Rule",
        required=True,
        help="Salary rule used to compute this line.",
    )
    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        help="Employee associated with this line.",
    )
    contract_id = fields.Many2one(
        "hr.version",
        required=True,
        index=True,
        help="Contract associated with this line.",
    )
    rate = fields.Float(
        string="Rate (%)",
        help="Percentage rate applied to this payslip line.",
        digits="Payroll Rate",
        default=100.0,
    )
    amount = fields.Float(
        digits="Payroll", help="Amount calculated for this payslip line."
    )
    quantity = fields.Float(
        digits="Payroll",
        default=1.0,
        help="Quantity factor applied to this payslip line.",
    )
    total = fields.Float(
        compute="_compute_total",
        help="Total computed amount for this payslip line.",
        digits="Payroll",
        store=True,
    )

    @api.depends("quantity", "amount", "rate")
    def _compute_total(self):
        """Function for compute total amount"""
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100

    @api.model_create_multi
    def create(self, vals_list):
        """Function for change value at the time of creation"""
        for values in vals_list:
            if "employee_id" not in values or "contract_id" not in values:
                payslip = self.env["hr.payslip"].browse(values.get("slip_id"))
                values["employee_id"] = (
                    values.get("employee_id") or payslip.employee_id.id
                )
                values["contract_id"] = (
                    values.get("contract_id")
                    or payslip.contract_id
                    and payslip.contract_id.id
                )
                if not values["contract_id"]:
                    raise UserError(
                        self.env._(
                            "You must set a contract to create a payslip line."
                        )
                    )
        return super().create(vals_list)
