# -*- coding: utf-8 -*-
#############################################################################
#   A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Raneesha M K (<https://www.cybrosys.com>)
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


class HrEmployee(models.Model):
    """Inherited the model to add some fields"""
    _inherit = 'hr.employee'

    insurance_percentage = fields.Float(string="Company Percentage ",
                                        help="Company insurance percentage")
    deduced_amount_per_month = fields.Float(string="Salary deduced per month",
                                            compute="_compute_deducted_amount",
                                            help="Amount that is deduced from "
                                                 "the salary per month")
    deduced_amount_per_year = fields.Float(string="Salary deduced per year",
                                           compute="_compute_deducted_amount",
                                           help="Amount that is deduced from "
                                                "the salary per year")
    insurance_ids = fields.One2many('hr.insurance',
                                    'employee_id',
                                    string="Insurance", help="Insurance",
                                    domain=[('state', '=', 'active')])

    def _compute_deducted_amount(self):
        """Used to get deduced amount"""
        current_date = fields.date.today()
        for emp in self:
            ins_amount = 0
            for ins in emp.insurance_ids:
                if ins.date_from <= current_date:
                    if ins.date_to >= current_date:
                        if ins.policy_coverage == 'monthly':
                            ins_amount = ins_amount + (ins.amount*12)
                        else:
                            ins_amount = ins_amount + ins.amount
            emp.deduced_amount_per_year = ins_amount-((ins_amount*emp.insurance_percentage)/100)
            emp.deduced_amount_per_month = emp.deduced_amount_per_year/12
