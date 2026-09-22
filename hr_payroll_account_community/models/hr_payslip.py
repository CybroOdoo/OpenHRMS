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
from odoo.exceptions import UserError
from markupsafe import Markup


class HrPayslip(models.Model):
    """ Extends the standard 'hr.payslip' model to include additional fields
        for accounting purposes."""
    _inherit = 'hr.payslip'

    date = fields.Date(string='Date Account',
                       help="Keep empty to use the period of the "
                            "validation(Payslip) date.")
    journal_id = fields.Many2one('account.journal',
                                 string='Salary Journal',
                                 required=True,
                                 help="Select Salary Journal",
                                 default=lambda self: self.env[
                                     'account.journal'].search(
                                     [('type', '=', 'general')],
                                     limit=1))
    move_id = fields.Many2one('account.move',
                              string='Accounting Entry',
                              readonly=True, copy=False,
                              help="Accounting entry associated with "
                                   "this record")
    paid = fields.Boolean(string='Made Payment Order', compute='_compute_paid', store=True, copy=False,
                          help="Automatically checked when the associated journal entry is paid.")
    payment_count = fields.Integer(compute='_compute_payment_count')

    def _compute_payment_count(self):
        """Compute the total number of payments linked to this payslip."""
        for slip in self:
            if slip.number:
                slip.payment_count = self.env['account.payment'].search_count([('memo', '=', slip.number)])
            else:
                slip.payment_count = 0

    @api.depends('move_id.payment_state')
    def _compute_paid(self):
        """Compute whether the payslip's associated journal entry is marked as paid."""
        for slip in self:
            slip.paid = slip.move_id and slip.move_id.payment_state in ('paid', 'in_payment', 'reversed') or False

    def action_open_journal_entry(self):
        """Open the corresponding accounting journal entry (move) for this payslip."""
        self.ensure_one()
        return {
            'name': _('Accounting Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.move_id.id,
        }

    def action_register_payment(self):
        """Register a payment for the net wage of this payslip in the accounting ledger."""
        self.ensure_one()
        
        if not self.move_id or self.move_id.state != 'posted':
            raise UserError(_("You can only register payment for posted journal entries."))
            
        journal = self.env['account.journal'].search([
            ('type', 'in', ('bank', 'cash')),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not journal:
            raise UserError(_("Please configure a Bank or Cash journal for the company '%s' to register a payment.") % self.company_id.name)
            
        payment_method_line = journal.outbound_payment_method_line_ids.filtered(lambda m: m.code == 'manual')
        if not payment_method_line and journal.outbound_payment_method_line_ids:
            payment_method_line = journal.outbound_payment_method_line_ids[0]
        
        payment = self.env['account.payment'].with_company(self.company_id).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.employee_id.work_contact_id.id,
            'amount': self.net_wage,
            'memo': self.number,
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'payment_method_line_id': payment_method_line.id if payment_method_line else False,
        })
        
        # Post the payment to move it to 'in_process'
        payment.action_post()
        
        # Reconcile the payment with the payslip's payable line
        payable_lines = self.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type in ('liability_payable', 'asset_receivable') 
            and not l.reconciled and l.credit > 0
        )
        
        for line in payable_lines:
            payment_lines = payment.move_id.line_ids.filtered(
                lambda l: l.account_id == line.account_id and not l.reconciled
            )
            if payment_lines:
                (line + payment_lines).reconcile()
                break
        
        # Post message in payment chatter linking back to the payslip
        body = Markup(_("This payment has been created from: <a href=# data-oe-model=hr.payslip data-oe-id=%d>%s</a>")) % (self.id, self.name)
        payment.message_post(body=body)
        

        
        return {
            'name': _('Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': payment.id,
        }

    def action_open_payment_wizard(self):
        """Open the batch payment wizard to register a manual payment."""
        self.ensure_one()
        if not self.move_id or self.move_id.state != 'posted':
            raise UserError(_("You can only register payment for posted journal entries."))
            
        action = self.env["ir.actions.actions"]._for_xml_id("hr_payroll_account_community.action_hr_batch_payment_wizard")
        action['context'] = {
            'active_model': 'hr.payslip',
            'active_ids': self.ids,
        }
        return action

    def action_open_payments(self):
        """Open the tree view displaying all payments associated with this payslip."""
        self.ensure_one()
        if not self.number:
            return {}
        payments = self.env['account.payment'].search([('memo', '=', self.number)])
        return {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', payments.ids)],
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to inject the default journal from context into the payslip."""
        journal_id = self.env.context.get('journal_id')
        if journal_id:
            for vals in vals_list:
                vals['journal_id'] = journal_id

        return super().create(vals_list)

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        """Triggered when the contract associated with the payroll slip is
            changed.This method is called when the 'contract_id' field is
            modified. It invokes the parent class's onchange method and then
            sets the 'journal_id' field based on the 'contract_id's journal or
            the default journal if no contract is selected."""
        super(HrPayslip, self).onchange_contract_id()
        self.journal_id = self.contract_id.journal_id.id or (
                not self.contract_id and
                self.default_get(['journal_id']).get('journal_id')
        )

    def action_payslip_cancel(self):
        """Cancel the payroll slip and associated accounting entries.This
        method cancels the current payroll slip by canceling its associated
        accounting entries (moves). If a move is in the 'posted' state, it is
        first uncanceled, then all moves are unlinked. Finally, the method
        calls the parent class's action_payslip_cancel method."""
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        moves.unlink()
        return super(HrPayslip, self).action_payslip_cancel()

    def _get_salary_rule_move_lines(self, line, amount):
        """
        Generate and return the default accounting move lines for a specific salary rule.
        
        This method serves as a generic extension hook. Downstream payroll accounting 
        modules (like Loans, Advances, or Insurance) can cleanly override this method 
        to intercept specific salary rules (e.g., based on line.code) and inject their 
        own custom, balanced accounting dictionaries natively during the payslip posting process.
        """
        res = []
        debit_account_id = line.salary_rule_id.account_debit_id.id
        credit_account_id = line.salary_rule_id.account_credit_id.id
        
        if line.code == 'NET' and credit_account_id and not line.salary_rule_id.account_credit_id.reconcile:
            raise UserError(_("The credit account on the NET salary rule is not reconciliable"))
            
        if debit_account_id:
            res.append((0, 0, {
                'name': line.name,
                'partner_id': line._get_partner_id(credit_account=False),
                'account_id': debit_account_id,
                'journal_id': self.journal_id.id,
                'date': self.date or self.date_to,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'tax_line_id': line.salary_rule_id.account_tax_id.id,
            }))
        if credit_account_id:
            res.append((0, 0, {
                'name': line.name,
                'partner_id': line._get_partner_id(credit_account=True),
                'account_id': credit_account_id,
                'journal_id': self.journal_id.id,
                'date': self.date or self.date_to,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'tax_line_id': line.salary_rule_id.account_tax_id.id,
            }))
        return res

    def action_payslip_done(self):
        """Finalize and post the payroll slip, creating accounting entries.This
         method is called when marking a payroll slip as done. It calculates
         the accounting entries based on the salary details, creates a move
         (journal entry),and posts it. If necessary, adjustment entries are
         added to balance the debit and credit amounts."""
        res = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            name = _('Payslip of %s') % slip.employee_id.name
            move_dict = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': slip.date or slip.date_to,
            }
            for line in slip.details_by_salary_rule_category_ids:
                amount = slip.company_id.currency_id.round(
                    slip.credit_note and -line.total or line.total)
                if slip.company_id.currency_id.is_zero(amount):
                    continue
                
                rule_lines = slip._get_salary_rule_move_lines(line, amount)
                for rule_line in rule_lines:
                    line_ids.append(rule_line)
                    debit_sum += rule_line[2].get('debit', 0.0) - rule_line[2].get('credit', 0.0)
            if slip.company_id.currency_id.compare_amounts(
                    credit_sum, debit_sum) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(
                        _('The Expense Journal "%s" has not properly '
                          'configured the Credit Account!') % (
                            slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': slip.date or slip.date_to,
                    'debit': 0.0,
                    'credit': slip.company_id.currency_id.round(
                        debit_sum - credit_sum),
                })
                line_ids.append(adjust_credit)
            elif slip.company_id.currency_id.compare_amounts(
                    debit_sum, credit_sum) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(
                        _('The Expense Journal "%s" has not properly '
                          'configured the Debit Account!') % (
                            slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': slip.date or slip.date_to,
                    'debit': slip.company_id.currency_id.round(
                        credit_sum - debit_sum),
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            slip.write({'move_id': move.id, 'date': slip.date or slip.date_to})
            if not move.line_ids:
                raise UserError(
                    _("As you installed the payroll accounting module you have"
                      " to choose Debit and Credit account for at least one "
                      "salary rule in the chosen Salary Structure."))
        return res

class AccountPayment(models.Model):
    """Extends account.payment to link back to the hr.payslip that generated it."""
    _inherit = 'account.payment'

    payslip_count = fields.Integer(compute='_compute_payslip_count')
    
    outstanding_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Outstanding Account",
        store=True,
        compute='_compute_outstanding_account_id',
        check_company=True)

    @api.depends('memo')
    def _compute_payslip_count(self):
        """Compute the number of payslips associated with this payment via the memo field."""
        for payment in self:
            if payment.memo:
                payment.payslip_count = self.env['hr.payslip'].search_count([('number', '=', payment.memo)])
            else:
                payment.payslip_count = 0

    @api.depends('payment_method_line_id', 'payslip_count')
    def _compute_outstanding_account_id(self):
        """Compute the outstanding account, using the journal's default account for payslip payments."""
        super(AccountPayment, self)._compute_outstanding_account_id()
        for pay in self:
            if pay.payslip_count > 0 and pay.journal_id.default_account_id:
                pay.outstanding_account_id = pay.journal_id.default_account_id

    def action_open_payslip(self):
        """Open the tree or form view of the payslips associated with this payment."""
        self.ensure_one()
        payslips = self.env['hr.payslip'].search([('number', '=', self.memo)])
        if payslips:
            return {
                'name': _('Payslip'),
                'type': 'ir.actions.act_window',
                'res_model': 'hr.payslip',
                'view_mode': 'form',
                'res_id': payslips[0].id,
            }
