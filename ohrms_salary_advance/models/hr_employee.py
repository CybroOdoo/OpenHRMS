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
from odoo import models

class HrEmployee(models.Model):
    """
    Inherited model hr.employee.
    Adds functionality related to managing salary advances for the employee.
    """
    _inherit = 'hr.employee'

    def _get_salary_advance_inputs(self, date_from, date_to):
        """
        Retrieves salary advance deductions for this employee within the given period.
        Returns a list of dictionaries suitable for hr.payslip.input.
        """
        self.ensure_one()
        inputs = []
        
        # Get active advances that are paid but not closed
        advances = self.env['salary.advance'].search([
            ('employee_id', '=', self.id),
            ('state', '=', 'paid'),
            ('company_id.salary_advance_auto_deduct', '=', True)
        ])
        
        for advance in advances:
            balance = advance.balance_amount
            if balance > 0:
                # In V1, we deduct the full balance or the fixed amount.
                # If there's a max fixed amount configured, we might limit it per month, 
                # but standard V1 is just full deduction of the remaining balance.
                inputs.append({
                    'name': f'Salary Advance ({advance.name})',
                    'code': 'SAR',
                    'amount': balance,
                    'advance_id': advance.id, # Custom reference if we need to link it
                })
                
        return inputs
