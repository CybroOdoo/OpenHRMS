# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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


class HrPayslip(models.Model):
    """ Extends the 'hr.payslip' model to include
    additional functionality related to employee loans."""
    _inherit = 'hr.payslip'

    def get_inputs(self, contracts, date_from, date_to):
        """Compute additional inputs for the employee payslip,
        considering active loans.
        :param contracts: Contract ID of the current employee.
        :param date_from: Start date of the payslip.
        :param date_to: End date of the payslip.
        :return: List of dictionaries representing additional inputs for
        the payslip."""
        res = super(HrPayslip, self).get_inputs(contracts, date_from,
                                                date_to)
        employee_id = contracts[0].employee_id if contracts \
            else self.employee_id
        loans = self.env['hr.loan'].search(
            [('employee_id', '=', employee_id.id), ('state', '=', 'approve')])
        
        date_from_dt = fields.Date.from_string(date_from)
        date_to_dt = fields.Date.from_string(date_to)
        
        total_loan_amount = 0.0
        first_loan_line_id = False
        
        for loan in loans:
            for loan_line in loan.loan_lines:
                loan_line_date = fields.Date.from_string(loan_line.date)
                if (date_from_dt <= loan_line_date <= date_to_dt and
                        not loan_line.paid):
                    total_loan_amount += loan_line.amount
                    if not first_loan_line_id:
                        first_loan_line_id = loan_line.id
                        
        if total_loan_amount > 0:
            lo_found = False
            for result in res:
                if result.get('code') == 'LO':
                    result['amount'] = total_loan_amount
                    result['loan_line_id'] = first_loan_line_id
                    lo_found = True
                    break
            if not lo_found:
                res.append({
                    'name': 'Loan Installment',
                    'code': 'LO',
                    'amount': total_loan_amount,
                    'contract_id': contracts[0].id if contracts else False,
                    'loan_line_id': first_loan_line_id
                })
        return res

    def action_payslip_done(self):
        """ Compute the loan amount and remaining amount while confirming
            the payslip"""
        for payslip in self:
            lo_lines = payslip.input_line_ids.filtered(lambda l: l.code == 'LO')
            if lo_lines:
                employee_id = payslip.contract_id.employee_id if payslip.contract_id else payslip.employee_id
                loans = self.env['hr.loan'].search([
                    ('employee_id', '=', employee_id.id),
                    ('state', '=', 'approve')
                ])
                
                date_from_dt = fields.Date.from_string(payslip.date_from)
                date_to_dt = fields.Date.from_string(payslip.date_to)
                
                for loan in loans:
                    for loan_line in loan.loan_lines:
                        loan_line_date = fields.Date.from_string(loan_line.date)
                        if date_from_dt <= loan_line_date <= date_to_dt and not loan_line.paid:
                            loan_line.paid = True
                            loan_line.loan_id._compute_total_amount()
        return super(HrPayslip, self).action_payslip_done()
