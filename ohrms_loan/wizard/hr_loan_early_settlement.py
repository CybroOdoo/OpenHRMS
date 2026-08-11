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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrLoanEarlySettlement(models.TransientModel):
    """
    Wizard for processing an early settlement of a loan.
    Allows either deducting the settlement amount from the next installments
    sequentially, or spreading the settlement deduction equally across all
    remaining unpaid installments.
    """
    _name = 'hr.loan.early.settlement'
    _description = 'Early Settlement Wizard'

    loan_id = fields.Many2one('hr.loan', string="Loan", required=True)
    amount = fields.Float(string="Settlement Amount", required=True)
    settlement_type = fields.Selection([
        ('next_installments', 'Deduct from Next Installment(s)'),
        ('spread_equally', 'Spread Equally Across Remaining Installments')
    ], string="Settlement Method", required=True, default='next_installments')

    @api.constrains('amount')
    def _check_amount(self):
        """
        Validate that the settlement amount entered is strictly positive.
        """
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Amount must be greater than zero."))

    def action_settle(self):
        """
        Process the early settlement according to the selected settlement method,
        adjusting the principal and interest amounts of remaining installments,
        or deleting them entirely if they are fully paid off by the settlement.
        """
        for rec in self:
            loan = rec.loan_id
            if loan.state != 'approve':
                raise ValidationError(_("Early settlement is only allowed for approved loans."))

            unpaid_lines = loan.loan_lines.filtered(lambda l: not l.paid)
            if not unpaid_lines:
                raise ValidationError(_("No unpaid installments to settle."))

            # Add a payment line
            payment_line = self.env['hr.loan.line'].with_context(early_settlement=True).create({
                'date': fields.Date.today(),
                'principal_amount': rec.amount,
                'interest_amount': 0.0,
                'amount': rec.amount,
                'employee_id': loan.employee_id.id,
                'loan_id': loan.id,
                'paid': True,
            })
            
            # If accounting module is installed, automatically generate the journal entry
            if hasattr(payment_line, 'action_paid_amount'):
                month_str = fields.Date.today().strftime('%b-%Y')
                payment_line.action_paid_amount(month_str)

            # Adjust unpaid lines based on principal
            remaining_s = rec.amount
            if rec.settlement_type == 'next_installments':
                for line in unpaid_lines.sorted('date'):
                    if round(remaining_s, 2) <= 0:
                        break
                    if line.principal_amount <= remaining_s + 0.001:
                        remaining_s -= line.principal_amount
                        line.with_context(early_settlement=True).unlink()
                    else:
                        line.with_context(early_settlement=True).write({'principal_amount': line.principal_amount - remaining_s})
                        remaining_s = 0

            elif rec.settlement_type == 'spread_equally':
                while round(remaining_s, 2) > 0:
                    existing_lines = unpaid_lines.filtered(lambda l: l.exists())
                    if not existing_lines:
                        break
                    per_line = remaining_s / len(existing_lines)
                    for line in existing_lines:
                        if round(remaining_s, 2) <= 0:
                            break
                        if line.principal_amount <= per_line + 0.001:
                            remaining_s -= line.principal_amount
                            line.with_context(early_settlement=True).unlink()
                        else:
                            line.with_context(early_settlement=True).write({'principal_amount': line.principal_amount - per_line})
                            remaining_s -= per_line

            # Recalculate interest for remaining lines
            remaining_unpaid = loan.loan_lines.filtered(lambda l: not l.paid)
            if remaining_unpaid:
                new_remaining_principal = sum(remaining_unpaid.mapped('principal_amount'))
                total_interest = 0.0
                if loan.interest_rate > 0:
                    if loan.interest_type == 'flat':
                        total_interest = new_remaining_principal * (loan.interest_rate / 100.0)
                    elif loan.interest_type == 'reducing':
                        temp_p = new_remaining_principal
                        for line in remaining_unpaid.sorted('date'):
                            total_interest += temp_p * (loan.interest_rate / 100.0)
                            temp_p -= line.principal_amount
                
                # Apply the new total interest equally across remaining lines
                interest_per_line = total_interest / len(remaining_unpaid)
                for line in remaining_unpaid:
                    line.with_context(early_settlement=True).write({'interest_amount': interest_per_line})

            loan._compute_total_amount()
        return {'type': 'ir.actions.act_window_close'}
