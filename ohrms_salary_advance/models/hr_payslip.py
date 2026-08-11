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
from odoo import models, fields


class HrPayslipInput(models.Model):
    """
    Inherited model hr.payslip.input.
    Adds advance_id to link deduction inputs to specific salary advances.
    """
    _inherit = 'hr.payslip.input'

    advance_id = fields.Many2one('salary.advance', string='Salary Advance',
                                 help="The salary advance this deduction is linked to.")


class HrPayslip(models.Model):
    """Class for the inherited model hr_payslip. Supering get_inputs() method
        inorder to add details of advance salary in the payslip."""
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """Supering get_inputs() method inorder to add details of advance
           salary in the payslip."""
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        
        contract = self.env['hr.version'].browse(contract_ids[0].id) if contract_ids else False
        employee = contract.employee_id if contract else self.employee_id
        
        if employee:
            advance_inputs = employee._get_salary_advance_inputs(date_from, date_to)
            for adv_input in advance_inputs:
                adv_input['contract_id'] = contract.id if contract else False
                # If an input with code SAR already exists, append to it, otherwise add new
                found = False
                for r in res:
                    if r.get('code') == 'SAR':
                        r['amount'] += adv_input['amount']
                        found = True
                        break
                if not found:
                    res.append(adv_input)
                    
        return res

    def action_payslip_done(self):
        """
        Supering action_payslip_done() method to close salary advances
        if their balance reaches zero after payslip deduction.
        """
        res = super(HrPayslip, self).action_payslip_done()
        for payslip in self:
            # Recompute deductions on advances to close them if fully paid
            advances = self.env['salary.advance'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', '=', 'paid')
            ])
            for advance in advances:
                if advance.balance_amount <= 0:
                    advance.state = 'closed'
        return res
