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


class Employee(models.Model):
    """
        Customizes the standard Odoo 'hr.employee' model to include additional
        fields for managing employee card numbers and WPS agent information.
    """
    _inherit = 'hr.employee'

    labour_card_number = fields.Char(
        string="Employee Card Number", size=14,
        help="Labour Card Number Of Employee (14 digits)")
    salary_card_number = fields.Char(
        string="Salary Card Number/Account Number", size=16,
        help="Salary card number or account number of employee (16 digits)")
    agent_id = fields.Many2one(
        'wps.agent', string="Agent/Bank",
        help="WPS Agent / Bank of Employee for UAE WPS")

    def write(self, vals):
        """Override write method to ensure correct
         formatting of card numbers."""
        self.formatting_card_numbers(vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to ensure correct
        formatting of card numbers."""
        for vals in vals_list:
            self.formatting_card_numbers(vals)
        return super().create(vals_list)

    def formatting_card_numbers(self, vals):
        """Ensure labour and salary card numbers are
        zero-padded to required lengths."""
        pad_length = {'labour_card_number': 14, 'salary_card_number': 16}
        for field in ['labour_card_number', 'salary_card_number']:
            if field in vals:
                value = vals[field]
                if not value:
                    continue
                required_len = pad_length[field]
                vals[field] = value.zfill(required_len) if len(value) < required_len else value
