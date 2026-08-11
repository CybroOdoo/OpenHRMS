# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models

class ResCompany(models.Model):
    """
    Inherited model res.company.
    Adds configuration fields for the salary advance module.
    """
    _inherit = 'res.company'

    salary_advance_enabled = fields.Boolean(
        string="Enable Salary Advance",
        default=True,
        help="Enable the salary advance feature for this company."
    )
    salary_advance_max_percent = fields.Float(
        string="Maximum Advance Percentage",
        default=50.0,
        help="Maximum percentage of the monthly wage that can be requested as an advance."
    )
    salary_advance_max_amount = fields.Float(
        string="Maximum Fixed Amount",
        default=0.0,
        help="Maximum fixed amount that can be requested as an advance. 0 means no limit."
    )
    salary_advance_min_days = fields.Integer(
        string="Minimum Employment Days",
        default=0,
        help="Minimum number of days an employee must be employed to be eligible for an advance."
    )
    salary_advance_multiple_active = fields.Boolean(
        string="Allow Multiple Active Advances",
        default=False,
        help="Allow employees to request a new advance while they still have an unpaid advance balance."
    )
    salary_advance_auto_deduct = fields.Boolean(
        string="Auto Deduct from Payroll",
        default=True,
        help="Automatically deduct outstanding salary advance balances during payslip computation."
    )

