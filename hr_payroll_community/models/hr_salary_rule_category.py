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
from odoo.exceptions import ValidationError


class HrSalaryRuleCategory(models.Model):
    """Create new model for Salary Rule Category"""

    _name = "hr.salary.rule.category"
    _description = "Salary Rule Category"

    name = fields.Char(
        required=True, translate=True, help="Name of the salary rule category."
    )
    code = fields.Char(required=True, help="Code of the salary rule category.")
    parent_id = fields.Many2one(
        "hr.salary.rule.category",
        help="Linking a salary category to its parent"
        "is used only for the reporting purpose.",
    )
    children_ids = fields.One2many(
        "hr.salary.rule.category",
        "parent_id",
        help="Child categories belonging to this category.",
    )
    note = fields.Text(
        string="Description", help="Description for Salary Category"
    )

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company.id,
        help="Company associated with this salary rule category.",
    )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        """Function to add constrains for parent_id field"""
        if self._has_cycle():
            raise ValidationError(
                self.env._(
                    "Error! You cannot create recursive "
                    "hierarchy of Salary Rule Category."
                )
            )
