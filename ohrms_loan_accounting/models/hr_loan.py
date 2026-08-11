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
from datetime import date
from odoo import fields, models
from odoo.exceptions import UserError


class HrLoanAcc(models.Model):
    """
    Inherit hr.loan to add accounting capabilities to the HR loan management process.
    Provides fields for configuring the Loan Journal, Loan Receivable Account, and 
    Interest Income Account. Modifies the approval workflow to automatically generate 
    the principal disbursement and interest recognition accounting entries.
    """
    _inherit = 'hr.loan'

    loan_receivable_account_id = fields.Many2one('account.account',
                                          domain="[('account_type', 'in', ('asset_current', 'asset_non_current', 'asset_receivable'))]",
                                          string="Loan Receivable Account",
                                          help="Employee loan receivable account")
    interest_income_account_id = fields.Many2one('account.account',
                                          domain="[('account_type', 'in', ('income', 'income_other'))]",
                                          string="Interest Income Account",
                                          help="Account for interest income")
    journal_id = fields.Many2one('account.journal', 
                                 domain="[('type', 'in', ('bank', 'cash'))]",
                                 string="Loan Journal",
                                 help="Journal for the loan")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', tracking=True,
        copy=False, help="State of the loan request")
        
    move_count = fields.Integer(string="Journal Entries", compute='_compute_move_count')

    def _compute_move_count(self):
        """
        Compute the total number of accounting journal entries (account.move) 
        associated with this loan.
        """
        for loan in self:
            moves = self.env['account.move'].search([('line_ids.loan_id', '=', loan.id)])
            loan.move_count = len(moves)

    def action_view_journal_entries(self):
        """
        Action to open the tree or form view of the accounting journal entries 
        (account.move) linked to this loan.
        """
        self.ensure_one()
        moves = self.env['account.move'].search([('line_ids.loan_id', '=', self.id)])
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        elif len(moves) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = moves.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_approve(self):
        """This creates account move for request."""
        loan_approve = self.env['ir.config_parameter'].sudo().get_param(
            'account.loan_approve') == 'True'
        contract_obj = self.env['hr.version'].search(
            [('employee_id', '=', self.employee_id.id)])
        if not contract_obj:
            raise UserError('You must Define a contract for employee')
        if not self.loan_lines:
            raise UserError('You must compute installment before Approved')
            
        loan_approval_threshold = float(self.env['ir.config_parameter'].sudo().get_param('account.loan_approval_threshold', default=0.0))
        
        if loan_approve and self.loan_amount >= loan_approval_threshold:
            self.write({'state': 'waiting_approval_2'})
        else:
            if (not self.loan_receivable_account_id or not self.journal_id):
                raise UserError(
                    "You must enter Loan Receivable account and journal to approve ")
            if not self.journal_id.default_account_id:
                raise UserError("You must configure a default account on the selected Journal.")
            if not self.loan_lines:
                raise UserError(
                    'You must compute Loan Request before Approved')
            timenow = date.today()
            for loan in self:
                amount = loan.loan_amount
                loan_name = loan.employee_id.name
                reference = loan.name
                journal_id = loan.journal_id.id
                debit_account_id = loan.loan_receivable_account_id.id
                credit_account_id = loan.journal_id.default_account_id.id
                debit_vals = {
                    'name': loan_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'loan_id': loan.id,
                }
                credit_vals = {
                    'name': loan_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'loan_id': loan.id,
                }
                vals = {
                    'narration': loan_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': timenow,
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                }
                move = self.env['account.move'].create(vals)
                move.action_post()
            self.write({'state': 'approve'})
        return True

    def action_double_approve(self):
        """This creates account move for request in case of double approval."""
        if (not self.loan_receivable_account_id or not self.journal_id):
            raise UserError(
                "You must enter Loan Receivable account and journal to approve ")
        if not self.journal_id.default_account_id:
            raise UserError("You must configure a default account on the selected Journal.")
        if not self.loan_lines:
            raise UserError('You must compute Loan Request before Approved')
        timenow = date.today()
        for loan in self:
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.journal_id.id
            debit_account_id = loan.loan_receivable_account_id.id
            credit_account_id = loan.journal_id.default_account_id.id
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'loan_id': loan.id,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'loan_id': loan.id,
            }
            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        self.write({'state': 'approve'})
        return True

    def action_topup_accounting(self, topup_amount):
        """This creates the account move for a loan top-up, disbursing the extra funds."""
        if (not self.loan_receivable_account_id or not self.journal_id):
            raise UserError(
                "You must enter Loan Receivable account and journal to process a top-up.")
        if not self.journal_id.default_account_id:
            raise UserError("You must configure a default account on the selected Journal.")
        
        timenow = date.today()
        for loan in self:
            loan_name = loan.employee_id.name
            reference = f"Top-Up: {loan.name}"
            journal_id = loan.journal_id.id
            debit_account_id = loan.loan_receivable_account_id.id
            credit_account_id = loan.journal_id.default_account_id.id
            
            debit_vals = {
                'name': f"Top-Up: {loan_name}",
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': topup_amount > 0.0 and topup_amount or 0.0,
                'credit': topup_amount < 0.0 and -topup_amount or 0.0,
                'loan_id': loan.id,
            }
            credit_vals = {
                'name': f"Top-Up: {loan_name}",
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': topup_amount < 0.0 and -topup_amount or 0.0,
                'credit': topup_amount > 0.0 and topup_amount or 0.0,
                'loan_id': loan.id,
            }
            vals = {
                'narration': f"Loan Top-Up for {loan_name}",
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        return True


class HrLoanLineAcc(models.Model):
    """ Creating account move for while confirm the loan lines"""
    _inherit = "hr.loan.line"

    def action_paid_amount(self, month):
        """This creates the account move line for payment of each installment.
            """
        if self.env.context.get('is_payslip'):
            return True
            
        timenow = date.today()
        for line in self:
            if line.loan_id.state != 'approve':
                raise UserError("Loan Request must be approved")
            if not line.loan_id.journal_id.default_account_id:
                raise UserError("You must configure a default account on the selected Journal.")
            amount = line.amount
            principal = line.principal_amount
            interest = line.interest_amount
            loan_name = line.employee_id.name
            reference = line.loan_id.name
            journal_id = line.loan_id.journal_id.id
            debit_account_id = line.loan_id.journal_id.default_account_id.id
            credit_receivable_account_id = line.loan_id.loan_receivable_account_id.id
            credit_interest_account_id = line.loan_id.interest_income_account_id.id
            line_ids = []
            
            # Debit: Bank/Treasury Account (Total Amount)
            line_ids.append((0, 0, {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'loan_id': line.loan_id.id,
            }))
            
            # Credit: Employee Loan Receivable (Principal Amount)
            if principal > 0:
                line_ids.append((0, 0, {
                    'name': loan_name,
                    'account_id': credit_receivable_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': principal < 0.0 and -principal or 0.0,
                    'credit': principal > 0.0 and principal or 0.0,
                    'loan_id': line.loan_id.id,
                }))

            # Credit: Interest Income Account (Interest Amount)
            if interest > 0:
                if not credit_interest_account_id:
                    raise UserError("You must configure an Interest Income account on the loan.")
                line_ids.append((0, 0, {
                    'name': loan_name + ' Interest',
                    'account_id': credit_interest_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': interest < 0.0 and -interest or 0.0,
                    'credit': interest > 0.0 and interest or 0.0,
                    'loan_id': line.loan_id.id,
                }))

            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': line_ids
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        return True
