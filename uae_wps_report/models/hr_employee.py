# -*- coding: utf-8 -*-
#############################################################################

#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: ASWIN A K (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models


class Employee(models.Model):
    """
        Customizes the standard Odoo 'hr.employee' model to include additional
        fields for managing employee card numbers and bank information.
    """
    _inherit = 'hr.employee'

    labour_card_number = fields.Char(
        string="Employee Card Number", size=14, required=True,
        help="Labour Card Number Of Employee")
    salary_card_number = fields.Char(
        string="Salary Card Number/Account Number", size=16, required=True,
        help="Salary card number or account number of employee")
    agent_id = fields.Many2one(
        'res.bank', string="Agent/Bank",
        required=True, help="Agent ID or bank ID of Employee")

    def write(self, vals):
        """Override write method to ensure correct
         formatting of card numbers."""
        self.formatting_card_numbers(vals)
        return super().write(vals)

    @api.model
    def create(self, vals):
        """Override create method to ensure correct
        formatting of card numbers."""
        self.formatting_card_numbers(vals)
        return super().create(vals)

    def formatting_card_numbers(self, vals):
        for field in ['labour_card_number', 'salary_card_number']:
            if field in vals:
                vals[field] = vals[field].zfill(
                    14 if vals[field] == 'labour_card_number' else 16) if len(
                    vals[field]) < 14 else vals[field]
