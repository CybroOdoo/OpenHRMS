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
import babel
from datetime import datetime, time
from odoo.exceptions import UserError
from odoo import fields, models, _


class HrSalaryRule(models.Model):
    """
    Inherit hr.salary.rule to add a boolean flag identifying loan deduction rules.
    This helps the payroll system differentiate loan deductions from regular deductions.
    """
    _inherit = 'hr.salary.rule'
    
    is_loan_rule = fields.Boolean(
        string="Is Loan Rule", 
        help="Check this if this rule is used for Loan Deductions. It will trigger the balanced loan accounting triplet."
    )


class HrPayslipAcc(models.Model):
    """
    Inherit hr.payslip to integrate loan accounting.
    Manages the deduction of loan installments from employee payslips and 
    generates the corresponding accounting journal entries for principal and interest.
    """
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        """Calculate the dates, mark loan lines as paid, and map accounting entries."""
        for slip in self:
            if slip.net_wage < 0:
                raise UserError(_("The Net Salary for %s is negative. The loan deduction exceeds the available salary. Please reduce the loan installment amount on the payslip.") % slip.employee_id.name)
                
            for line in slip.input_line_ids:
                date_from = slip.date_from
                tym = datetime.combine(fields.Date.from_string(date_from), time.min)
                locale = self.env.context.get('lang') or 'en_US'
                month = str(babel.dates.format_date(date=tym, format='MMMM-y', locale=locale))
                if line.loan_line_id:
                    line.loan_line_id.with_context(is_payslip=True).action_paid_amount(month)
                    
        return super(HrPayslipAcc, self).action_payslip_done()

    def _get_salary_rule_move_lines(self, line, amount):
        """
        Override to intercept accounting entries for loan deductions.
        Instead of a single credit to a clearing account, this splits the deduction 
        into Principal (credited to the Loan Receivable Account) and Interest 
        (credited to the Interest Income Account) based on the associated loan installments.
        """
        res = super(HrPayslipAcc, self)._get_salary_rule_move_lines(line, amount)
        
        # Check if it's a loan rule (either via the new boolean flag or fallback to legacy 'LO' code)
        is_loan = False
        if hasattr(line.salary_rule_id, 'is_loan_rule') and line.salary_rule_id.is_loan_rule:
            is_loan = True
        elif line.code == 'LO':
            is_loan = True
            
        if is_loan:
            loan_inputs = self.input_line_ids.filtered(lambda l: l.loan_line_id)
            if not loan_inputs or not res:
                return res
                
            clearing_account_id = res[0][2]['account_id']
            
            new_lines = []
            currency = self.company_id.currency_id or self.env.company.currency_id
            
            target_total = abs(amount)
            current_total = 0.0
            
            for i, input_line in enumerate(loan_inputs):
                loan = input_line.loan_line_id.loan_id
                principal = currency.round(input_line.loan_line_id.principal_amount)
                interest = currency.round(input_line.loan_line_id.interest_amount)
                
                # Absorb penny rounding differences into the final principal amount 
                # so the generated credits exactly match the payslip deduction amount
                if i == len(loan_inputs) - 1:
                    remaining = target_total - current_total
                    diff = remaining - (principal + interest)
                    if abs(diff) < 1.0:
                        principal += diff
                        
                current_total += principal + interest
                
                # Option B: Doublet Approach (No clearing debit)
                # We do not generate a Debit to Salary Payable because the core Net Salary rule 
                # evaluates to the net amount, inherently providing the necessary balance.
                
                if principal > 0:
                    new_lines.append((0, 0, {
                        'name': f"{line.name} ({loan.name}) Principal Recovery",
                        'partner_id': res[0][2]['partner_id'],
                        'account_id': loan.loan_receivable_account_id.id,
                        'journal_id': res[0][2]['journal_id'],
                        'date': res[0][2]['date'],
                        'debit': 0.0,
                        'credit': principal,
                        'tax_line_id': res[0][2]['tax_line_id'],
                    }))
                if interest > 0:
                    if not loan.interest_income_account_id:
                        raise UserError(_("Interest Income Account must be configured on loan %s") % loan.name)
                    new_lines.append((0, 0, {
                        'name': f"{line.name} ({loan.name}) Interest Recovery",
                        'partner_id': res[0][2]['partner_id'],
                        'account_id': loan.interest_income_account_id.id,
                        'journal_id': res[0][2]['journal_id'],
                        'date': res[0][2]['date'],
                        'debit': 0.0,
                        'credit': interest,
                        'tax_line_id': res[0][2]['tax_line_id'],
                    }))
            return new_lines
        return res